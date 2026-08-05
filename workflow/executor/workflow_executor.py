import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Set

from capabilities.service import CapabilityService
from interaction.service import InteractionEngineService
from verification.service import GoalVerificationService
from workflow.executor.cancellation import CancellationToken
from workflow.executor.checkpoint_manager import WorkflowCheckpointManager
from workflow.executor.configuration import WorkflowExecutorConfig
from workflow.executor.events import ExecutorEvent
from workflow.executor.models import (
    WorkflowExecutionResult,
    WorkflowExecutionState,
    WorkflowProgress,
    WorkflowTaskExecution,
    WorkflowTaskState,
)
from workflow.executor.progress_tracker import WorkflowProgressTracker
from workflow.executor.scheduler import ExecutionScheduler
from workflow.executor.state_manager import WorkflowStateManager
from workflow.executor.task_executor import TaskExecutor
from workflow.executor.timeout_manager import TimeoutManager
from workflow.graph.graph import TaskGraphEngine
from workflow.graph.models import NodeStatus

logger = logging.getLogger("AURA.Workflow.Executor.Engine")


class WorkflowExecutor:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[WorkflowExecutorConfig] = None,
        capability_service: Optional[CapabilityService] = None,
        interaction_service: Optional[InteractionEngineService] = None,
        verification_service: Optional[GoalVerificationService] = None,
        tool_registry: Any = None,
        observer: Any = None,
    ):
        self.bus = bus
        self.config = config or WorkflowExecutorConfig()
        self.workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        self.tool_registry = tool_registry
        self.observer = observer

        self.cancellation_token = CancellationToken()
        self.timeout_manager = TimeoutManager()
        self.state_manager = WorkflowStateManager()
        self.progress_tracker = WorkflowProgressTracker()
        self.checkpoint_manager = WorkflowCheckpointManager()
        self.scheduler = ExecutionScheduler(max_concurrency=self.config.max_parallel_tasks)
        self.task_executor = TaskExecutor(
            capability_service=capability_service,
            interaction_service=interaction_service,
            verification_service=verification_service,
        )

        self._task_execs: Dict[str, WorkflowTaskExecution] = {}
        self._completed_tasks: Set[str] = set()
        self._failed_tasks: Set[str] = set()
        self._task_outputs: Dict[str, Dict[str, Any]] = {}
        self._verification_results: Dict[str, Dict[str, Any]] = {}

    async def execute_graph(self, task_graph_engine: TaskGraphEngine) -> WorkflowExecutionResult:
        start_time = time.time()
        self.state_manager.set_workflow_state(WorkflowExecutionState.RUNNING)
        self._publish_event(ExecutorEvent.WORKFLOW_STARTED, {"workflow_id": self.workflow_id})

        all_task_ids = list(task_graph_engine.nodes.keys())
        for tid, node in task_graph_engine.nodes.items():
            self._task_execs[tid] = WorkflowTaskExecution(
                task_id=tid,
                name=node.name,
                capability=node.capability,
                inputs=node.inputs,
                outputs=node.outputs,
                status=WorkflowTaskState.PENDING,
            )

        stages = task_graph_engine.get_parallel_execution_stages()

        for stage in stages:
            if self.cancellation_token.is_cancelled():
                msg = "Workflow execution cancelled by user"
                self.state_manager.set_workflow_state(WorkflowExecutionState.CANCELLED)
                self._publish_event(ExecutorEvent.WORKFLOW_CANCELLED, {"workflow_id": self.workflow_id})
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return WorkflowExecutionResult(
                    workflow_id=self.workflow_id,
                    success=False,
                    state=WorkflowExecutionState.CANCELLED,
                    completed_task_ids=list(self._completed_tasks),
                    failed_task_ids=list(self._failed_tasks),
                    duration_ms=duration_ms,
                    message=msg,
                )

            async_tasks = [self._execute_single_task_with_retry(tid) for tid in stage.task_ids]
            results = await asyncio.gather(*async_tasks, return_exceptions=True)

            for tid, res in zip(stage.task_ids, results):
                if isinstance(res, Exception) or not (isinstance(res, bool) and res):
                    self._failed_tasks.add(tid)

            if self.config.auto_checkpoint:
                ckpt = self.checkpoint_manager.create_checkpoint(
                    workflow_id=self.workflow_id,
                    completed_tasks=list(self._completed_tasks),
                    task_outputs=self._task_outputs,
                    current_context={"stage_idx": stage.stage_index},
                    verification_results=self._verification_results,
                )
                self._publish_event(ExecutorEvent.CHECKPOINT_CREATED, ckpt.to_dict())

            if self._failed_tasks:
                msg = f"Workflow failed due to task failures: {list(self._failed_tasks)}"
                self.state_manager.set_workflow_state(WorkflowExecutionState.FAILED)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return WorkflowExecutionResult(
                    workflow_id=self.workflow_id,
                    success=False,
                    state=WorkflowExecutionState.FAILED,
                    completed_task_ids=list(self._completed_tasks),
                    failed_task_ids=list(self._failed_tasks),
                    duration_ms=duration_ms,
                    message=msg,
                )

        duration_ms = round((time.time() - start_time) * 1000, 2)
        self.state_manager.set_workflow_state(WorkflowExecutionState.COMPLETED)
        res = WorkflowExecutionResult(
            workflow_id=self.workflow_id,
            success=True,
            state=WorkflowExecutionState.COMPLETED,
            completed_task_ids=list(self._completed_tasks),
            failed_task_ids=[],
            duration_ms=duration_ms,
            message="Workflow execution completed successfully",
            data={"task_outputs": self._task_outputs},
        )
        self._publish_event(ExecutorEvent.WORKFLOW_COMPLETED, res.to_dict())
        return res

    async def _execute_single_task_with_retry(self, task_id: str) -> bool:
        task_exec = self._task_execs[task_id]
        self.state_manager.set_task_state(task_id, WorkflowTaskState.RUNNING)
        self._publish_event(ExecutorEvent.TASK_STARTED, task_exec.to_dict())

        retries = 0
        max_retries = self.config.max_task_retries

        while retries <= max_retries:
            if self.cancellation_token.is_cancelled():
                self.state_manager.set_task_state(task_id, WorkflowTaskState.CANCELLED)
                return False

            try:
                ok, msg, outputs = await self.scheduler.run_task(
                    self.timeout_manager.execute_with_timeout(
                        self.task_executor.execute_task(task_exec),
                        timeout_sec=self.config.task_timeout_sec,
                    )
                )

                if ok:
                    self.state_manager.set_task_state(task_id, WorkflowTaskState.COMPLETED)
                    self._completed_tasks.add(task_id)
                    self._task_outputs[task_id] = outputs
                    self._publish_event(ExecutorEvent.TASK_COMPLETED, task_exec.to_dict())
                    return True

            except Exception as e:
                msg = str(e)

            retries += 1
            if retries <= max_retries:
                task_exec.retries_attempted = retries
                self._publish_event(ExecutorEvent.TASK_RETRIED, {"task_id": task_id, "retry_count": retries})
                await asyncio.sleep(0.1)

        self.state_manager.set_task_state(task_id, WorkflowTaskState.FAILED, error_msg=msg)
        self._failed_tasks.add(task_id)
        self._publish_event(ExecutorEvent.TASK_FAILED, {"task_id": task_id, "error": msg})
        return False

    def cancel(self) -> None:
        self.cancellation_token.cancel()

    def execute_workflow(self, workflow_or_graph: Any) -> WorkflowExecutionResult:
        """Backwards compatible execution interface supporting sync and async callers."""
        graph_engine = workflow_or_graph if hasattr(workflow_or_graph, "nodes") else TaskGraphEngine()
        if isinstance(workflow_or_graph, dict) and "tasks" in workflow_or_graph:
            graph_engine.build_from_planner_tasks(workflow_or_graph["tasks"])

        try:
            loop = asyncio.get_running_loop()
            return self.execute_graph(graph_engine)
        except RuntimeError:
            return asyncio.run(self.execute_graph(graph_engine))

    def get_progress(self) -> WorkflowProgress:
        return self.progress_tracker.get_progress(
            tasks=self._task_execs,
            all_task_ids=list(self._task_execs.keys()),
        )

    def _publish_event(self, event: ExecutorEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish executor event '{event.value}': {e}")
