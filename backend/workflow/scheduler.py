import logging
from typing import Dict, List, Optional
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.Scheduler")


class WorkflowScheduler:
    """Scheduler managing workflow execution queues (Immediate, Delayed, Recurring)."""

    def __init__(self):
        self.queue: List[Workflow] = []

    def schedule_immediate(self, workflow: Workflow) -> None:
        self.queue.append(workflow)
        logger.info(f"Scheduled workflow '{workflow.workflow_id}' for immediate execution.")

    def get_next(self) -> Optional[Workflow]:
        if self.queue:
            return self.queue.pop(0)
        return None

