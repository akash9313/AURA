import logging
from typing import Dict, List, Optional
from workflow.workflow import Workflow

logger = logging.getLogger("AURA.Workflow.History")


class WorkflowHistoryManager:
    """Historical archive recorder for completed and failed workflows."""

    def __init__(self):
        self.history: Dict[str, Workflow] = {}

    def archive(self, workflow: Workflow) -> None:
        self.history[workflow.workflow_id] = workflow
        logger.info(f"Archived workflow '{workflow.workflow_id}' to history store.")

    def get(self, workflow_id: str) -> Optional[Workflow]:
        return self.history.get(workflow_id)
