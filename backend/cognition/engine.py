import logging
import time
from typing import Any, Dict, Optional

from agent.orchestrator import AgentOrchestrator
from agent.workflow import Workflow
from cognition.confidence import ConfidenceEngine
from cognition.context import CognitiveContext
from cognition.decision import DecisionEngine
from cognition.evaluator import PlanEvaluator
from cognition.goal_manager import GoalManager, GoalStatus, GoalType
from cognition.models import CognitiveDecision, ConfidenceScore, ReflectionRecord
from cognition.planner import CognitivePlanner
from cognition.reasoning import ReasoningEngine
from cognition.reflection import ReflectionEngine
from cognition.state import CognitiveStateManager
from memory.manager import MemoryManager
from tools.registry import ToolRegistry

logger = logging.getLogger("AURA.Cognition.Engine")


class CognitiveEngine:
    """
    Master Cognitive Engine of AURA.

    Orchestrates the 8-stage Cognitive Execution Loop:
    Understand -> Retrieve -> Goal -> Plan -> Evaluate -> Execute -> Reflect -> Learn
    """

    def __init__(
        self,
        registry: ToolRegistry = None,
        memory: MemoryManager = None,
        orchestrator: AgentOrchestrator = None,
        bus = None
    ):
        self.registry = registry if registry is not None else ToolRegistry(auto_discover=True)
        self.memory = memory if memory is not None else MemoryManager()
        self.orchestrator = orchestrator if orchestrator is not None else AgentOrchestrator(
            registry=self.registry,
            memory=self.memory,
            bus=bus
        )
        self.bus = bus

        self.state_manager = CognitiveStateManager()
        self.goal_manager = GoalManager()
        self.confidence_engine = ConfidenceEngine()
        self.decision_engine = DecisionEngine()
        self.reasoning_engine = ReasoningEngine(memory=self.memory, decision_engine=self.decision_engine)
        self.evaluator = PlanEvaluator(confidence_engine=self.confidence_engine)
        self.planner = CognitivePlanner()
        self.reflection_engine = ReflectionEngine(memory=self.memory)

    def process_request(self, user_input: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Main Entry Point: Process user input through the 8-stage Cognitive Loop.

        Args:
            user_input (str): Natural language instruction.
            conversation_id (str, optional): Active session conversation ID.

        Returns:
            Dict[str, Any]: Cognitive result payload containing answer, workflow, and reflection.
        """
        logger.info(f"🧠 CognitiveEngine initiating cognitive loop for: '{user_input}'")
        ctx = CognitiveContext(request_id=f"req_{int(time.time())}")

        # Stage 1 & 2: Understand & Retrieve Context/Memory
        ctx.log_reasoning("UNDERSTAND_AND_RETRIEVE", {"input": user_input})
        synthesis = self.reasoning_engine.analyze_intent(user_input)
        decision: CognitiveDecision = synthesis["decision"]
        ctx.log_decision(decision)

        # Stage 3: Determine Goal
        goal_obj = self.goal_manager.create_goal(user_input, goal_type=GoalType.SHORT_TERM)
        self.state_manager.set_goal(goal_obj.goal_id)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.GOAL_CREATED, goal_obj.to_dict())

        # Stage 4: Generate Plan
        ctx.log_reasoning("GENERATE_PLAN", {"goal_id": goal_obj.goal_id})
        workflow: Workflow = self.planner.generate_plan(user_input, decision)
        self.state_manager.set_workflow(workflow.workflow_id)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.PLAN_CREATED, workflow.to_dict())

        # Stage 5: Evaluate Plan
        ctx.log_reasoning("EVALUATE_PLAN", {"workflow_id": workflow.workflow_id})
        is_acceptable, conf_score = self.evaluator.evaluate_workflow(workflow)
        self.state_manager.update_confidence(conf_score.score, conf_score.reason, conf_score.risk_level)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.DECISION_MADE, conf_score.to_dict())

        # Stage 6: Execute Plan via Agent Orchestrator
        ctx.log_reasoning("EXECUTE", {"workflow_id": workflow.workflow_id})
        self.goal_manager.update_status(goal_obj.goal_id, GoalStatus.ACTIVE)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.EXECUTION_STARTED, {"goal_id": goal_obj.goal_id})

        evaluated_workflow = self.orchestrator.process_goal(user_input, conversation_id=conversation_id)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.EXECUTION_FINISHED, {"workflow_id": evaluated_workflow.workflow_id})

        # Stage 7 & 8: Reflect & Store Learning
        ctx.log_reasoning("REFLECT_AND_LEARN", {"workflow_id": evaluated_workflow.workflow_id})
        reflection: ReflectionRecord = self.reflection_engine.reflect_on_workflow(evaluated_workflow)
        ctx.set_reflection(reflection)

        final_status = GoalStatus.COMPLETED if reflection.was_successful else GoalStatus.FAILED
        self.goal_manager.update_status(goal_obj.goal_id, final_status)

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.REFLECTION_COMPLETED, reflection.to_dict())
            self.bus.publish(Event.LEARNING_COMPLETED, {"goal_id": goal_obj.goal_id, "insights": reflection.memory_insights})

        # Extract final output string
        task_outputs = [t.result for t in evaluated_workflow.tasks if t.result is not None]
        final_answer = str(task_outputs[-1]) if task_outputs else reflection.summary

        return {
            "answer": final_answer,
            "goal": goal_obj.to_dict(),
            "workflow": evaluated_workflow.to_dict(),
            "confidence": conf_score.to_dict(),
            "reflection": reflection.to_dict(),
            "context_summary": ctx.get_summary()
        }
