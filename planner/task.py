import logging
from typing import Any, Dict, List, Optional

from planner.models import PlannerTask

logger = logging.getLogger("AURA.Planner.Task")


class TaskBuilder:
    def __init__(self, description: str, capability: str):
        self._task = PlannerTask(
            description=description,
            capability_required=capability,
        )

    def with_inputs(self, inputs: Dict[str, Any]) -> "TaskBuilder":
        self._task.inputs.update(inputs)
        return self

    def with_outputs(self, outputs: Dict[str, Any]) -> "TaskBuilder":
        self._task.outputs.update(outputs)
        return self

    def depends_on(self, task_ids: List[str]) -> "TaskBuilder":
        self._task.dependencies.extend(task_ids)
        return self

    def with_verification(self, rule: Dict[str, Any]) -> "TaskBuilder":
        self._task.verification_rule.update(rule)
        return self

    def with_retry(self, max_retries: int = 2, backoff_sec: float = 1.0) -> "TaskBuilder":
        self._task.retry_policy = {"max_retries": max_retries, "backoff_sec": backoff_sec}
        return self

    def mark_recovery_point(self, is_recovery: bool = True) -> "TaskBuilder":
        self._task.is_recovery_point = is_recovery
        return self

    def build(self) -> PlannerTask:
        return self._task
