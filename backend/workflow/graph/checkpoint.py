"""
Graph Checkpoint Manager.
Generates and restores recovery checkpoints capturing completed tasks, outputs, context, and verification results.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set

from workflow.graph.models import GraphCheckpoint, GraphNode, NodeStatus

logger = logging.getLogger("AURA.Workflow.Graph.Checkpoint")


class CheckpointManager:
    """
    Manages GraphCheckpoint creation and restoration for workflow interruption recovery.
    """

    def __init__(self):
        self._checkpoints: Dict[str, GraphCheckpoint] = {}

    def create_checkpoint(
        self,
        graph_id: str,
        completed_tasks: List[str],
        task_outputs: Dict[str, Dict[str, Any]],
        current_context: Dict[str, Any],
        verification_results: Dict[str, Dict[str, Any]],
    ) -> GraphCheckpoint:
        """
        Create and store a recovery checkpoint.

        Returns:
            GraphCheckpoint instance.
        """
        ckpt = GraphCheckpoint(
            graph_id=graph_id,
            completed_tasks=list(completed_tasks),
            task_outputs=dict(task_outputs),
            current_context=dict(current_context),
            verification_results=dict(verification_results),
        )
        self._checkpoints[ckpt.checkpoint_id] = ckpt
        logger.info(f"Created GraphCheckpoint '{ckpt.checkpoint_id}' with {len(completed_tasks)} completed tasks")
        return ckpt

    def get_checkpoint(self, checkpoint_id: str) -> Optional[GraphCheckpoint]:
        """Retrieve checkpoint by ID."""
        return self._checkpoints.get(checkpoint_id)

    def restore_graph_state(
        self,
        nodes: Dict[str, GraphNode],
        checkpoint: GraphCheckpoint,
    ) -> Set[str]:
        """
        Restore node statuses and outputs from checkpoint.

        Returns:
            Set of completed task IDs.
        """
        completed = set(checkpoint.completed_tasks)
        for nid, node in nodes.items():
            if nid in completed:
                node.status = NodeStatus.COMPLETED
                if nid in checkpoint.task_outputs:
                    node.outputs.update(checkpoint.task_outputs[nid])

        logger.info(f"Restored graph state from checkpoint '{checkpoint.checkpoint_id}': {len(completed)} nodes completed")
        return completed
