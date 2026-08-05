"""
Workflow Evaluator Engine.
Evaluates mission success rates, failure root causes, bottleneck tasks, and capability reliability metrics.
"""

import logging
from typing import Any, Dict, List, Tuple

from reflection.models import TaskMetric

logger = logging.getLogger("AURA.Reflection.Evaluator")


class WorkflowEvaluator:
    """
    Evaluates workflow execution performance.
    """

    def evaluate_performance(
        self,
        workflow_result: Any,
        metrics: List[TaskMetric],
    ) -> Tuple[float, float, List[str]]:
        """
        Evaluate overall mission performance metrics.

        Returns:
            Tuple of (success_rate: float, total_duration_ms: float, failure_reasons: List[str])
        """
        success = getattr(workflow_result, "success", True)
        duration_ms = getattr(workflow_result, "duration_ms", 0.0)
        failure_reasons = []

        if not success:
            msg = getattr(workflow_result, "message", "Workflow failed")
            failure_reasons.append(msg)

        total_tasks = len(metrics)
        completed = [t for t in metrics if t.status == "completed"]
        success_rate = round(len(completed) / total_tasks, 2) if total_tasks > 0 else (1.0 if success else 0.0)

        logger.info(f"Evaluated workflow: Success Rate = {success_rate}, Total Duration = {duration_ms}ms")
        return (success_rate, duration_ms, failure_reasons)
