"""
Task Graph Validator.
Validates DAG structural integrity, missing dependencies, and cycle detection.
"""

import logging
from typing import Dict, List, Set, Tuple

from workflow.graph.models import GraphNode

logger = logging.getLogger("AURA.Workflow.Graph.Validator")


class GraphValidator:
    """
    Validates Task Graph DAG structures and dependencies.
    """

    def validate_graph(self, nodes: Dict[str, GraphNode]) -> Tuple[bool, List[str]]:
        """
        Validate nodes dictionary for cycles and missing dependencies.

        Returns:
            Tuple of (is_valid: bool, List of error messages)
        """
        errors = []

        if not nodes:
            errors.append("Graph contains no nodes")
            return (False, errors)

        # 1. Dependency validation
        for nid, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id not in nodes:
                    errors.append(f"Node '{nid}' references non-existent dependency '{dep_id}'")

        # 2. Cycle detection
        if self.has_cycle(nodes):
            errors.append("Cyclic dependency detected in workflow task DAG graph")

        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"Task Graph with {len(nodes)} nodes validated successfully")
        else:
            logger.warning(f"Task Graph validation failed: {errors}")

        return (is_valid, errors)

    def has_cycle(self, nodes: Dict[str, GraphNode]) -> bool:
        """Kahn's DFS cycle detection."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            node = nodes.get(node_id)
            if node:
                for dep_id in node.dependencies:
                    if dep_id not in visited:
                        if dfs(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for nid in nodes:
            if nid not in visited:
                if dfs(nid):
                    return True
        return False
