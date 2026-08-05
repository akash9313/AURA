import logging
from typing import Any, Dict, List, Optional

from workflow.graph.checkpoint import CheckpointManager as TaskGraphCheckpointManager
from workflow.graph.models import GraphCheckpoint

logger = logging.getLogger("AURA.Workflow.Executor.Checkpoint")


class WorkflowCheckpointManager:
    def __init__(self):
        self.underlying_manager = TaskGraphCheckpointManager()

    def create_checkpoint(
        self,
        workflow_id: str,
        completed_tasks: List[str],
        task_outputs: Dict[str, Dict[str, Any]],
        current_context: Dict[str, Any],
        verification_results: Dict[str, Dict[str, Any]],
    ) -> GraphCheckpoint:
        return self.underlying_manager.create_checkpoint(
            graph_id=workflow_id,
            completed_tasks=completed_tasks,
            task_outputs=task_outputs,
            current_context=current_context,
            verification_results=verification_results,
        )

    def get_checkpoint(self, checkpoint_id: str) -> Optional[GraphCheckpoint]:
        return self.underlying_manager.get_checkpoint(checkpoint_id)
