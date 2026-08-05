import logging
import time
from typing import Any, Dict, Optional

from workflow.integration.events import WorkflowIntegrationEvent

logger = logging.getLogger("AURA.Workflow.Integration.ProgressReporter")


class ProgressReporter:
    def __init__(self, bus: Any = None):
        self.bus = bus

    def report_mission_started(self, mission_id: str, total_tasks: int) -> None:
        self._publish(WorkflowIntegrationEvent.MISSION_STARTED, {
            "mission_id": mission_id,
            "total_tasks": total_tasks,
            "timestamp": time.time(),
        })

    def report_task_started(self, mission_id: str, task_id: str, name: str) -> None:
        self._publish(WorkflowIntegrationEvent.TASK_STARTED, {
            "mission_id": mission_id,
            "task_id": task_id,
            "name": name,
            "timestamp": time.time(),
        })

    def report_task_completed(self, mission_id: str, task_id: str, name: str, duration_sec: float) -> None:
        self._publish(WorkflowIntegrationEvent.TASK_COMPLETED, {
            "mission_id": mission_id,
            "task_id": task_id,
            "name": name,
            "duration_sec": duration_sec,
            "timestamp": time.time(),
        })

    def report_task_failed(self, mission_id: str, task_id: str, name: str, error: str) -> None:
        self._publish(WorkflowIntegrationEvent.TASK_FAILED, {
            "mission_id": mission_id,
            "task_id": task_id,
            "name": name,
            "error": error,
            "timestamp": time.time(),
        })

    def report_mission_progress(self, mission_id: str, completed_count: int, total_tasks: int) -> None:
        pct = round((completed_count / total_tasks * 100) if total_tasks > 0 else 100, 1)
        self._publish(WorkflowIntegrationEvent.MISSION_PROGRESS, {
            "mission_id": mission_id,
            "completed_count": completed_count,
            "total_tasks": total_tasks,
            "percentage": pct,
            "timestamp": time.time(),
        })

    def report_mission_completed(self, mission_id: str, execution_time_sec: float) -> None:
        self._publish(WorkflowIntegrationEvent.MISSION_COMPLETED, {
            "mission_id": mission_id,
            "execution_time_sec": execution_time_sec,
            "timestamp": time.time(),
        })

    def report_mission_cancelled(self, mission_id: str, reason: str = "Cancelled by user") -> None:
        self._publish(WorkflowIntegrationEvent.MISSION_CANCELLED, {
            "mission_id": mission_id,
            "reason": reason,
            "timestamp": time.time(),
        })

    def _publish(self, event: WorkflowIntegrationEvent, payload: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, payload)
            except Exception as e:
                logger.error(f"Failed to publish progress event '{event.value}': {e}")
