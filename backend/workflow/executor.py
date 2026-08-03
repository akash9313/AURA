import logging
import time
from typing import Dict, Optional
from tools.registry import ToolRegistry
from workflow.events import WorkflowEvent
from workflow.models import TaskState, WorkflowState
from workflow.observer import WorkflowObserver
from workflow.recovery import WorkflowRecoveryManager
from workflow.task import WorkflowTask
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Executor")


class WorkflowExecutor:
    """
    Executes tasks in a Workflow graph, managing retries, timeouts, and observers.
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None, observer: Optional[WorkflowObserver] = None):
        self.tool_registry = tool_registry if tool_registry is not None else ToolRegistry()
        self.observer = observer if observer is not None else WorkflowObserver()
        self.recovery = WorkflowRecoveryManager()

    def execute_workflow(self, workflow: Workflow) -> Workflow:
        """
        Execute workflow tasks sequentially or concurrently based on DAG readiness.

        Args:
            workflow (Workflow): Ready workflow instance.

        Returns:
            Workflow: Updated workflow instance upon completion or failure.
        """
        workflow.state = WorkflowState.RUNNING
        workflow.metrics.started_at = time.time()
        self.observer.notify_event(WorkflowEvent.WORKFLOW_STARTED, {"workflow_id": workflow.workflow_id})

        while not workflow.is_finished():
            ready_tasks = workflow.get_ready_tasks()

            if not ready_tasks:
                # If no tasks ready and not finished, we hit a deadlock or unhandled failure
                break

            for task in ready_tasks:
                if workflow.state in (WorkflowState.CANCELLED, WorkflowState.PAUSED):
                    logger.info(f"Workflow '{workflow.workflow_id}' execution interrupted ({workflow.state.value})")
                    return workflow

                self._execute_single_task(workflow, task)

        # Check overall workflow status
        has_failed_task = any(t.state == TaskState.FAILED for t in workflow.tasks.values())
        if has_failed_task:
            workflow.state = WorkflowState.FAILED
            self.observer.notify_event(WorkflowEvent.TASK_FAILED, {"workflow_id": workflow.workflow_id})
        else:
            workflow.state = WorkflowState.COMPLETED
            self.observer.notify_event(WorkflowEvent.WORKFLOW_COMPLETED, {"workflow_id": workflow.workflow_id})

        workflow.metrics.completed_at = time.time()
        workflow.metrics.total_duration_ms = (workflow.metrics.completed_at - workflow.metrics.started_at) * 1000.0
        return workflow

    def _execute_single_task(self, workflow: Workflow, task: WorkflowTask) -> None:
        """Execute single task node with retry shielding."""
        task.state = TaskState.RUNNING
        task.metrics.start_time = time.time()
        self.observer.notify_event(WorkflowEvent.TASK_STARTED, {"workflow_id": workflow.workflow_id, "task_id": task.task_id})

        tool = self.tool_registry.get(task.tool)
        if not tool:
            err = f"Tool '{task.tool}' is not registered in ToolRegistry."
            logger.error(err)
            task.metrics.error_message = err
            can_retry = self.recovery.handle_task_failure(task)
            if can_retry and task.state == TaskState.RETRYING:
                self._execute_single_task(workflow, task)
            return

        try:
            res = tool.execute(task.parameters)
            task.metrics.end_time = time.time()
            task.metrics.execution_time_ms = (task.metrics.end_time - task.metrics.start_time) * 1000.0

            if res.success:
                task.state = TaskState.COMPLETED
                task.result = {"message": res.message, "data": getattr(res, "data", {})}
                workflow.metrics.completed_tasks += 1
                self.observer.notify_event(WorkflowEvent.TASK_COMPLETED, {"workflow_id": workflow.workflow_id, "task_id": task.task_id})
            else:
                task.metrics.error_message = res.message
                can_retry = self.recovery.handle_task_failure(task)
                if can_retry and task.state == TaskState.RETRYING:
                    workflow.metrics.retried_tasks += 1
                    self._execute_single_task(workflow, task)
                else:
                    workflow.metrics.failed_tasks += 1

        except Exception as e:
            task.metrics.error_message = str(e)
            logger.error(f"Execution error on task '{task.task_id}': {e}")
            can_retry = self.recovery.handle_task_failure(task)
            if can_retry and task.state == TaskState.RETRYING:
                workflow.metrics.retried_tasks += 1
                self._execute_single_task(workflow, task)
            else:
                workflow.metrics.failed_tasks += 1
