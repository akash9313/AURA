import logging
from typing import Any, Dict, List, Optional, Set

from workflow.graph.models import GraphCheckpoint, GraphNode, NodeStatus

logger = logging.getLogger("AURA.Workflow.Graph.Checkpoint")


class CheckpointManager:
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
        ckpt = GraphCheckpoint(
            graph_id=graph_id,
            completed_tasks=list(completed_tasks),
            task_outputs=dict(task_outputs),
            current_context=dict(current_context),
            verification_results=dict(verification_results),
        )
        self._checkpoints[ckpt.checkpoint_id] = ckpt
        return ckpt

    def get_checkpoint(self, checkpoint_id: str) -> Optional[GraphCheckpoint]:
        return self._checkpoints.get(checkpoint_id)

    def restore_graph_state(
        self,
        nodes: Dict[str, GraphNode],
        checkpoint: GraphCheckpoint,
    ) -> Set[str]:
        completed = set(checkpoint.completed_tasks)
        for nid, node in nodes.items():
            if nid in completed:
                node.status = NodeStatus.COMPLETED
                if nid in checkpoint.task_outputs:
                    node.outputs.update(checkpoint.task_outputs[nid])
        return completed
