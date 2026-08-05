from enum import Enum


class GraphEvent(Enum):
    GRAPH_CREATED = "graph_created"
    GRAPH_VALIDATED = "graph_validated"
    GRAPH_FAILED = "graph_failed"
    NODE_READY = "node_ready"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    CHECKPOINT_CREATED = "checkpoint_created"
