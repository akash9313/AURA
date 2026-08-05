import logging
from typing import Any, Dict, List

from reflection.models import TaskMetric

logger = logging.getLogger("AURA.Reflection.Metrics")


class MetricsCollector:
    def collect_task_metrics(self, workflow_result: Any) -> List[TaskMetric]:
        metrics: List[TaskMetric] = []
        data = getattr(workflow_result, "data", {}) or {}
        outputs = data.get("task_outputs", {})

        completed = getattr(workflow_result, "completed_task_ids", []) or []
        failed = getattr(workflow_result, "failed_task_ids", []) or []

        for tid in completed:
            out = outputs.get(tid, {})
            duration = out.get("duration_ms", 1.0)
            metrics.append(
                TaskMetric(
                    task_id=tid,
                    capability=out.get("capability", "unknown_capability"),
                    duration_ms=duration,
                    retries=out.get("retries", 0),
                    status="completed",
                )
            )

        for tid in failed:
            out = outputs.get(tid, {})
            metrics.append(
                TaskMetric(
                    task_id=tid,
                    capability=out.get("capability", "unknown_capability"),
                    duration_ms=out.get("duration_ms", 0.0),
                    retries=out.get("retries", 1),
                    status="failed",
                )
            )

        return metrics
