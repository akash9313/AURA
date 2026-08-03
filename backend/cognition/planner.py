import logging
from agent.planner import AgentPlanner
from agent.workflow import Workflow
from cognition.models import CognitiveDecision

logger = logging.getLogger("AURA.Cognition.Planner")


class CognitivePlanner:
    """
    Coordinates goal decomposition with the Agent Engine's AgentPlanner.
    """

    def __init__(self, agent_planner: AgentPlanner = None):
        self.agent_planner = agent_planner if agent_planner is not None else AgentPlanner()

    def generate_plan(self, goal_title: str, decision: CognitiveDecision) -> Workflow:
        """
        Construct a multi-step Workflow matching the decision strategy.

        Args:
            goal_title (str): High-level goal.
            decision (CognitiveDecision): Decision Engine strategy selection.

        Returns:
            Workflow: Constructed workflow task graph.
        """
        logger.info(f"CognitivePlanner generating workflow plan for goal: '{goal_title}'")

        # Delegate workflow decomposition to AgentPlanner
        workflow = self.agent_planner.plan_goal(goal_title)
        return workflow
