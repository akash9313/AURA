import logging
from typing import Dict

from workflow.executor.models import (
    WorkflowExecutionState,
    WorkflowTaskExecution,
    WorkflowTaskState,
)

logger = logging.getLogger("AURA.Workflow.Executor.StateManager")


class WorkflowStateManager:
    def __init__(self):
        self.workflow_state = WorkflowExecutionState.PENDING
        self.task_states: Dict[str, WorkflowTaskExecution] = {}

    def set_workflow_state(self, new_state: WorkflowExecutionState) -> None:
        self.workflow_state = new_state

    def set_task_state(self, task_id: str, new_state: WorkflowTaskState, error_msg: str = None) -> None:
        if task_id in self.task_states:
            task_exec = self.task_states[task_id]
            task_exec.status = new_state
            if error_msg:
                task_exec.error_message = error_msg
