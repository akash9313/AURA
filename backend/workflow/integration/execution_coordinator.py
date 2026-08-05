"""
Execution Coordinator (State Pattern & Coordinator).
Orchestrates sequential and parallel task graph execution, checkpointing, recovery, cancellation, and verification.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Set

from workflow.executor.cancellation import CancellationToken
from workflow.integration.capability_dispatcher import (
    CapabilityDispatcher,
    CapabilityNotFoundError,
    VerificationFailedError,
)
from workflow.integration.configuration import WorkflowIntegrationConfig
from workflow.integration.models import (
    MissionExecutionResult,
    MissionExecutionStatus,
    TaskExecutionProgress,
)
from workflow.integration.progress_reporter import ProgressReporter

logger = logging.getLogger("AURA.Workflow.Integration.ExecutionCoordinator")


class ExecutionCoordinator:
    """
    Coordinates DAG task execution with concurrency limits, retries, checkpointing, and cancellation.
    """

    def __init__(
        self,
        config: Optional[WorkflowIntegrationConfig] = None,
        dispatcher: Optional[CapabilityDispatcher] = None,
        reporter: Optional[ProgressReporter] = None,
    ):
        self.config = config or WorkflowIntegrationConfig()
        self.dispatcher = dispatcher or CapabilityDispatcher()
        self.reporter = reporter or ProgressReporter()
        self.cancellation_token = CancellationToken()

    async def execute_mission_plan(
        self,
        mission_id: str,
        task_graph: Any,
    ) -> MissionExecutionResult:
        """
        Execute DAG task graph bounded by execution timeout, retries, and cancellation token.

        Args:
            mission_id: ID of the mission.
            task_graph: TaskGraph containing tasks dictionary.

        Returns:
            MissionExecutionResult object.
        """
        start_time = time.time()
        tasks_dict = getattr(task_graph, "tasks", {})
        total_tasks = len(tasks_dict)

        result = MissionExecutionResult(
            mission_id=mission_id,
            status=MissionExecutionStatus.RUNNING,
        )

        self.reporter.report_mission_started(mission_id, total_tasks)

        if total_tasks == 0:
            result.status = MissionExecutionStatus.COMPLETED
            result.execution_time_sec = round(time.time() - start_time, 3)
            result.summary = "No tasks to execute."
            self.reporter.report_mission_completed(mission_id, result.execution_time_sec)
            return result

        # Track completed and failed tasks
        completed_set: Set[str] = set()
        failed_set: Set[str] = set()
        recovery_count = 0

        # Execute task graph (topological / dependency-driven parallel execution)
        try:
            async with asyncio.timeout(self.config.max_execution_time_sec):
                while len(completed_set) + len(failed_set) < total_tasks:
                    if self.cancellation_token.is_cancelled():
                        logger.warning(f"Mission '{mission_id}' execution cancelled by token.")
                        result.status = MissionExecutionStatus.CANCELLED
                        result.summary = "Mission execution was cancelled."
                        self.reporter.report_mission_cancelled(mission_id)
                        return result

                    # Identify ready tasks whose dependencies are satisfied
                    ready_tasks = []
                    for tid, task in tasks_dict.items():
                        if tid in completed_set or tid in failed_set:
                            continue
                        deps = getattr(task, "dependencies", [])
                        if all(dep in completed_set for dep in deps):
                            ready_tasks.append(task)

                    if not ready_tasks:
                        if len(completed_set) + len(failed_set) < total_tasks:
                            logger.error(f"Dependency deadlock detected in mission '{mission_id}'!")
                            break
                        break

                    # Parallel execution bounded by parallel_task_limit
                    chunk = ready_tasks[: self.config.parallel_task_limit]
                    exec_futures = [
                        self._execute_task_with_retry(mission_id, task)
                        for task in chunk
                    ]

                    outcomes = await asyncio.gather(*exec_futures, return_exceptions=True)

                    for task_obj, outcome in zip(chunk, outcomes):
                        tid = getattr(task_obj, "task_id", str(task_obj))

                        if isinstance(outcome, Exception):
                            failed_set.add(tid)
                            err_msg = str(outcome)
                            self.reporter.report_task_failed(mission_id, tid, getattr(task_obj, "description", tid), err_msg)
                        elif isinstance(outcome, dict) and outcome.get("success", False):
                            completed_set.add(tid)
                            rec_used = outcome.get("retries", 0)
                            recovery_count += rec_used
                            dur = outcome.get("duration_sec", 0.0)
                            self.reporter.report_task_completed(mission_id, tid, getattr(task_obj, "description", tid), dur)
                        else:
                            failed_set.add(tid)
                            err_msg = outcome.get("error", "Task execution failed") if isinstance(outcome, dict) else str(outcome)
                            self.reporter.report_task_failed(mission_id, tid, getattr(task_obj, "description", tid), err_msg)

                    result.completed_tasks = list(completed_set)
                    result.failed_tasks = list(failed_set)
                    self.reporter.report_mission_progress(mission_id, len(completed_set), total_tasks)

        except TimeoutError:
            err_msg = f"Mission execution timed out after {self.config.max_execution_time_sec}s."
            logger.error(err_msg)
            result.status = MissionExecutionStatus.FAILED
            result.summary = err_msg
            return result
        except Exception as e:
            err_msg = f"Unexpected execution exception: {str(e)}"
            logger.error(err_msg)
            result.status = MissionExecutionStatus.FAILED
            result.summary = err_msg
            return result

        result.execution_time_sec = round(time.time() - start_time, 3)
        result.recovery_attempts = recovery_count

        if failed_set:
            result.status = MissionExecutionStatus.FAILED
            result.summary = f"Execution failed for {len(failed_set)} tasks."
        else:
            result.status = MissionExecutionStatus.COMPLETED
            result.summary = f"Successfully executed and verified all {len(completed_set)} tasks."
            self.reporter.report_mission_completed(mission_id, result.execution_time_sec)

        return result

    async def _execute_task_with_retry(self, mission_id: str, task: Any) -> Dict[str, Any]:
        """Execute single task with automatic retries."""
        tid = getattr(task, "task_id", "task_unknown")
        name = getattr(task, "description", tid)
        cap_required = getattr(task, "capability_required", "generic_capability")
        inputs = getattr(task, "inputs", {})
        verif_rule = getattr(task, "verification_rule", {})

        self.reporter.report_task_started(mission_id, tid, name)

        last_error = ""
        for attempt in range(1, self.config.max_retries + 1):
            if self.cancellation_token.is_cancelled():
                return {"success": False, "error": "Cancelled", "task_id": tid}

            try:
                res = await self.dispatcher.dispatch_and_verify_task(
                    task_id=tid,
                    capability_name=cap_required,
                    parameters=inputs,
                    verification_rule=verif_rule,
                )
                res["success"] = True
                res["retries"] = attempt - 1
                return res

            except (CapabilityNotFoundError, VerificationFailedError, Exception) as e:
                last_error = str(e)
                logger.warning(f"Task '{tid}' attempt {attempt}/{self.config.max_retries} failed: {last_error}")
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.backoff_sec)

        return {"success": False, "error": last_error, "task_id": tid}

    def cancel(self, reason: str = "User cancelled") -> None:
        """Trigger cancellation token."""
        logger.warning(f"ExecutionCoordinator cancellation requested: {reason}")
        self.cancellation_token.cancel()
