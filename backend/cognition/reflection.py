import logging
from typing import List
from agent.state import TaskStatus, WorkflowState
from agent.workflow import Workflow
from cognition.models import ReflectionRecord
from memory.manager import MemoryManager

logger = logging.getLogger("AURA.Cognition.Reflection")


class ReflectionEngine:
    """
    Analyzes completed/failed workflow executions, detects failures, and generates memory learnings.
    """

    def __init__(self, memory: MemoryManager = None):
        self.memory = memory if memory is not None else MemoryManager()

    def reflect_on_workflow(self, workflow: Workflow) -> ReflectionRecord:
        """
        Evaluate workflow execution results, extract learnings, and update memory.

        Args:
            workflow (Workflow): Evaluated workflow object.

        Returns:
            ReflectionRecord: Structured reflection record with insights.
        """
        is_success = workflow.status == WorkflowState.COMPLETED
        failed_tools: List[str] = []
        improvements: List[str] = []
        insights: List[str] = []

        for task in workflow.tasks:
            if task.status == TaskStatus.FAILED:
                failed_tools.append(task.tool_name)
                improvements.append(f"Task '{task.task_id}' using tool '{task.tool_name}' failed after {task.retry_count} retries.")

        if is_success:
            summary = f"Goal '{workflow.goal}' achieved successfully with {len(workflow.tasks)} task(s)."
            insights.append(f"Successfully executed workflow '{workflow.workflow_id}' for goal '{workflow.goal}'.")
        else:
            summary = f"Goal '{workflow.goal}' failed due to failures in tools: {failed_tools}."
            improvements.append("Re-evaluate tool parameter validation or fallback strategy.")

        record = ReflectionRecord(
            was_successful=is_success,
            failed_tools=failed_tools,
            plan_improvements=improvements,
            should_update_memory=True,
            memory_insights=insights,
            summary=summary
        )

        # Store insight in Working Memory
        try:
            self.memory.working.set_variable("last_reflection", record.to_dict())
            logger.info(f"ReflectionEngine saved learning insight for goal '{workflow.goal}'.")
        except Exception as e:
            logger.warning(f"Failed to persist reflection insight to memory: {e}")

        return record
