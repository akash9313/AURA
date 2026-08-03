import logging
from typing import Any, Dict, Optional
from agent.context import AgentContext
from agent.executor import TaskExecutor
from agent.history import AgentHistory
from agent.planner import AgentPlanner
from agent.result import TaskResult
from agent.retry import RetryStrategy
from agent.state import TaskStatus, WorkflowState
from agent.task import Task
from agent.validator import TaskValidator
from agent.workflow import Workflow
from memory.manager import MemoryManager
from tools.registry import ToolRegistry

logger = logging.getLogger("AURA.Agent.Orchestrator")


class AgentOrchestrator:
    """
    The 'CEO' Orchestrator Engine of AURA.

    Coordinates multi-step workflows, task graph execution, exponential backoff retries,
    validation, execution history logging, memory persistence, and event notifications.
    """

    def __init__(
        self,
        registry: ToolRegistry = None,
        memory: MemoryManager = None,
        bus = None
    ):
        self.registry = registry if registry is not None else ToolRegistry(auto_discover=True)
        self.memory = memory if memory is not None else MemoryManager()
        self.bus = bus

        self.planner = AgentPlanner()
        self.executor = TaskExecutor(registry=self.registry)
        self.validator = TaskValidator(registry=self.registry)
        self.retry_strategy = RetryStrategy()
        self.history = AgentHistory()

    def process_goal(self, goal: str, conversation_id: str = None) -> Workflow:
        """
        Main Entry Point: Process user goal instruction end-to-end.

        Args:
            goal (str): High-level user goal.
            conversation_id (str, optional): Active session conversation ID.

        Returns:
            Workflow: Completed or evaluated workflow object.
        """
        logger.info(f"👑 AgentOrchestrator received goal: '{goal}'")
        self.history.log_event("GOAL_RECEIVED", {"goal": goal})

        # 1. Create Context & Plan Workflow
        context = AgentContext(goal=goal, conversation_id=conversation_id or "")
        workflow = self.planner.plan_goal(goal)
        context.workflow = workflow

        self.history.log_event("WORKFLOW_PLANNED", {
            "workflow_id": workflow.workflow_id,
            "tasks_count": len(workflow.tasks)
        })

        if self.bus:
            from core.events import Event
            self.bus.publish(Event.WORKFLOW_CREATED, workflow.to_dict())

        # 2. Execute Task Graph Iteratively
        workflow.status = WorkflowState.RUNNING

        while not workflow.is_finished():
            ready_tasks = workflow.get_ready_tasks()
            if not ready_tasks:

                # Check if any tasks failed or remain pending
                failed_tasks = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
                pending_tasks = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]

                if failed_tasks:
                    workflow.status = WorkflowState.FAILED
                    logger.error(f"Workflow '{workflow.workflow_id}' failed due to task failures.")
                elif pending_tasks:
                    workflow.status = WorkflowState.FAILED
                    logger.error(f"Workflow '{workflow.workflow_id}' deadlocked with unresolvable dependencies.")
                else:
                    workflow.status = WorkflowState.COMPLETED
                    logger.info(f"🎉 Workflow '{workflow.workflow_id}' completed successfully!")
                break

            # Process ready task with highest priority
            ready_tasks.sort(key=lambda t: t.priority)
            current_task = ready_tasks[0]

            self._execute_single_task(current_task, workflow, context)

        # 3. Save Summary into Memory Engine
        self._persist_workflow_memory(workflow)

        # 4. Publish Final Event
        if self.bus:
            from core.events import Event
            event_type = Event.WORKFLOW_COMPLETED if workflow.status == WorkflowState.COMPLETED else Event.WORKFLOW_FAILED
            self.bus.publish(event_type, workflow.to_dict())

        return workflow

    def _execute_single_task(self, task: Task, workflow: Workflow, context: AgentContext) -> None:
        """Validate, execute, observe, and handle retries for a single task."""
        completed_ids = [t.task_id for t in workflow.tasks if t.status == TaskStatus.COMPLETED]
        is_valid, msg = self.validator.validate_task(task, completed_ids)

        if not is_valid:
            task.status = TaskStatus.FAILED
            self.history.log_event("TASK_INVALID", {"task_id": task.task_id, "reason": msg})
            return

        task.status = TaskStatus.RUNNING
        self.history.log_event("TASK_STARTED", {"task_id": task.task_id, "tool": task.tool_name})

        # Retry Loop with Exponential Backoff
        for attempt in range(task.max_retries + 1):
            task.retry_count = attempt
            result: TaskResult = self.executor.execute_task(task)

            if result.success:
                task.status = TaskStatus.COMPLETED
                task.result = result.output
                context.set_output(task.task_id, result.output)
                self.history.log_event("TASK_COMPLETED", {
                    "task_id": task.task_id,
                    "output": str(result.output)[:100],
                    "time": result.execution_time
                })
                return
            else:
                logger.warning(f"Task '{task.task_id}' attempt {attempt + 1} failed: {result.error}")
                if attempt < task.max_retries:
                    task.status = TaskStatus.WAITING
                    delay = self.retry_strategy.get_delay(attempt)
                    logger.info(f"Retrying task '{task.task_id}' in {delay:.2f}s...")

        # Failed after all retries
        task.status = TaskStatus.FAILED
        self.history.log_event("TASK_FAILED", {"task_id": task.task_id, "error": result.error})

    def _persist_workflow_memory(self, workflow: Workflow) -> None:
        """Store workflow completion metrics in Memory Engine."""
        try:
            self.memory.working.set_task(workflow.goal)
            self.memory.working.set_variable("workflow_id", workflow.workflow_id)
            self.memory.working.set_variable("status", workflow.status.value)
            logger.info(f"Persisted workflow '{workflow.workflow_id}' to Memory Engine.")
        except Exception as e:
            logger.warning(f"Failed to persist workflow memory: {e}")
