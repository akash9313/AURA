"""
Workflow State Manager (State Pattern).
Manages valid state transitions for tasks and overall workflows.
Lifecycle: Pending -> Ready -> Running -> Verifying -> Completed / Failed / Cancelled
"""

import logging
from typing import Dict

from workflow.executor.models import (
    WorkflowExecutionState,
    WorkflowTaskExecution,
    WorkflowTaskState,
)

logger = logging.getLogger("AURA.Workflow.Executor.StateManager")


class WorkflowStateManager:
    """
    Manages task and workflow lifecycle state transitions.
    """

    def __init__(self):
        self.workflow_state = WorkflowExecutionState.PENDING
        self.task_states: Dict[str, WorkflowTaskExecution] = {}

    def set_workflow_state(self, new_state: WorkflowExecutionState) -> None:
        logger.info(f"Workflow state transition: {self.workflow_state.value} -> {new_state.value}")
        self.workflow_state = new_state

    def set_task_state(self, task_id: str, new_state: WorkflowTaskState, error_msg: str = None) -> None:
        if task_id in self.task_states:
            task_exec = self.task_states[task_id]
            logger.debug(f"Task '{task_id}' transition: {task_exec.status.value} -> {new_state.value}")
            task_exec.status = new_state
            if error_msg:
                task_exec.error_message = error_msg
