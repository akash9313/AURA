import logging
import time
from typing import Callable, Dict, List, Optional
from workflow.events import WorkflowEvent
from workflow.task import WorkflowTask
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Observer")


class WorkflowObserver:
    """Monitors task execution progress, performance telemetry, and errors."""

    def __init__(self, bus=None):
        self.bus = bus

    def notify_event(self, event: WorkflowEvent, payload: Dict):
        logger.info(f"Observer Event [{event.value}]: {payload}")
        if self.bus:
            self.bus.publish(event.value, payload)
