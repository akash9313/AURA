import logging
from typing import Dict, Optional
from workflow.models import TaskState, WorkflowState
from workflow.task import WorkflowTask
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Recovery")


class WorkflowRecoveryManager:
    """Manages crash recovery, task retries, checkpoints, and execution resuming."""

    def handle_task_failure(self, task: WorkflowTask) -> bool:
        """
        Evaluate task failure for retry or fallback.

        Returns:
            bool: True if task can be retried.
        """
        if task.metrics.retry_count < task.max_retries:
            task.metrics.retry_count += 1
            task.state = TaskState.RETRYING
            logger.info(f"Retrying task '{task.task_id}' ({task.metrics.retry_count}/{task.max_retries})")
            return True

        if task.optional:
            task.state = TaskState.SKIPPED
            logger.info(f"Skipping optional failed task '{task.task_id}'")
            return True

        task.state = TaskState.FAILED
        logger.error(f"Task '{task.task_id}' failed permanently after {task.metrics.retry_count} retries.")
        return False
