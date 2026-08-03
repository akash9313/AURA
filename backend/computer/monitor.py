import logging
import time
from typing import Dict, Any
from computer.models import AutomationResult

logger = logging.getLogger("AURA.Computer.Monitor")


class ComputerMonitor:
    """Latency and retry telemetry recorder for computer automation."""

    def __init__(self):
        self.total_actions: int = 0
        self.successful_actions: int = 0
        self.failed_actions: int = 0

    def record_result(self, result: AutomationResult) -> None:
        self.total_actions += 1
        if result.success:
            self.successful_actions += 1
        else:
            self.failed_actions += 1
        logger.info(f"Automation Metric: Action '{result.action}' | Success: {result.success} | Latency: {result.execution_time_ms:.1f}ms")
