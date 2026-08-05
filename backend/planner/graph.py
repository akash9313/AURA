"""
Task Graph DAG Builder.
Assembles directed acyclic graph (DAG) task structures, validates dependencies, and detects cycles.
"""

import logging
from typing import Dict, List, Set

from planner.models import PlannerTask, TaskGraph

logger = logging.getLogger("AURA.Planner.Graph")


class TaskGraphBuilder:
    """
    Constructs and validates TaskGraph DAG structures.
    """

    def build_graph(self, tasks: List[PlannerTask]) -> TaskGraph:
        """
        Build TaskGraph from list of PlannerTasks and validate DAG.

        Args:
            tasks: List of PlannerTask instances.

        Returns:
            Constructed TaskGraph.

        Raises:
            ValueError if cycle detected in graph.
        """
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

        # Validate DAG (Cycle detection)
        if self._has_cycle(graph):
            logger.error("Cyclic dependency detected in task graph!")
            raise ValueError("Cyclic dependency detected in workflow task DAG graph")

        logger.info(f"TaskGraph successfully built with {len(graph.tasks)} tasks and {len(graph.root_task_ids)} roots")
        return graph

    def _has_cycle(self, graph: TaskGraph) -> bool:
        """Kahn's Algorithm / DFS for cycle detection in DAG."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            task = graph.get_task(task_id)
            if task:
                for dep_id in task.dependencies:
                    if dep_id not in visited:
                        if dfs(dep_id):
                            return True
                    elif dep_id in rec_stack:
                        return True

            rec_stack.remove(task_id)
            return False

        for tid in graph.tasks:
            if tid not in visited:
                if dfs(tid):
                    return True
        return False
