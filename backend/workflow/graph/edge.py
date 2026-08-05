"""
Graph Edge Builder.
Constructs GraphEdge dependency edges (Hard, Soft, Conditional, Parallel).
"""

import logging
from typing import Optional

from workflow.graph.models import EdgeType, GraphEdge

logger = logging.getLogger("AURA.Workflow.Graph.Edge")


class GraphEdgeBuilder:
    """
    Builder Pattern for GraphEdge instances.
    """

    def __init__(self, source_id: str, target_id: str):
        self._edge = GraphEdge(source_id=source_id, target_id=target_id)

    def with_type(self, edge_type: EdgeType) -> "GraphEdgeBuilder":
        self._edge.edge_type = edge_type
        return self

    def with_condition(self, condition_expr: str) -> "GraphEdgeBuilder":
        self._edge.edge_type = EdgeType.CONDITIONAL
        self._edge.condition_expr = condition_expr
        return self

    def build(self) -> GraphEdge:
        logger.debug(f"Built GraphEdge: '{self._edge.source_id}' -> '{self._edge.target_id}' ({self._edge.edge_type.value})")
        return self._edge
