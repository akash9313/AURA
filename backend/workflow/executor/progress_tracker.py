"""
Workflow Progress Tracker.
Exposes real-time progress model (current task, completed tasks, remaining tasks, estimated time, success rate, current capability).
"""

import logging
from typing import Dict, List, Optional

from workflow.executor.models import WorkflowProgress, WorkflowTaskExecution, WorkflowTaskState

logger = logging.getLogger("AURA.Workflow.Executor.ProgressTracker")


class WorkflowProgressTracker:
    """
    Tracks and computes real-time workflow progress metrics.
    """

    def get_progress(
        self,
        tasks: Dict[str, WorkflowTaskExecution],
        all_task_ids: List[str],
        current_task_id: Optional[str] = None,
    ) -> WorkflowProgress:
        """
        Compute progress model snapshot.

        Returns:
            WorkflowProgress dataclass instance.
        """
        completed = [tid for tid, t in tasks.items() if t.status == WorkflowTaskState.COMPLETED]
        failed = [tid for tid, t in tasks.items() if t.status == WorkflowTaskState.FAILED]
        remaining = [tid for tid in all_task_ids if tid not in completed and tid not in failed]

        total_processed = len(completed) + len(failed)
        success_rate = round(len(completed) / total_processed, 2) if total_processed > 0 else 1.0

        current_cap = None
        if current_task_id and current_task_id in tasks:
            current_cap = tasks[current_task_id].capability

        est_time = round(len(remaining) * 1.5, 1)

        return WorkflowProgress(
            current_task=current_task_id,
            completed_tasks=completed,
            remaining_tasks=remaining,
            estimated_remaining_time=est_time,
            success_rate=success_rate,
            current_capability=current_cap,
        )
