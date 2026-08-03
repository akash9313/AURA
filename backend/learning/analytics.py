import logging
from typing import Any, Dict

logger = logging.getLogger("AURA.Learning.Analytics")


class LearningAnalyticsRecorder:
    """Tracks learning telemetry: success rates, completion trends, tool usage frequency, and overrides."""

    def __init__(self):
        self.total_workflows: int = 0
        self.successful_workflows: int = 0
        self.failed_workflows: int = 0
        self.user_overrides: int = 0

    def record_workflow_result(self, success: bool) -> None:
        self.total_workflows += 1
        if success:
            self.successful_workflows += 1
        else:
            self.failed_workflows += 1

    def record_override(self) -> None:
        self.user_overrides += 1

    def get_summary(self) -> Dict[str, Any]:

        rate = (self.successful_workflows / float(self.total_workflows)) * 100.0 if self.total_workflows > 0 else 0.0
        return {
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "failed_workflows": self.failed_workflows,
            "success_rate_percent": round(rate, 2),
            "user_overrides": self.user_overrides,
        }
