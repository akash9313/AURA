import logging
from typing import Dict, List, Set

from planner.models import PlannerTask, TaskGraph

logger = logging.getLogger("AURA.Planner.Graph")


class TaskGraphBuilder:
    def build_graph(self, tasks: List[PlannerTask]) -> TaskGraph:
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

        if self._has_cycle(graph):
            raise ValueError("Cyclic dependency detected in workflow task DAG graph")

        return graph

    def _has_cycle(self, graph: TaskGraph) -> bool:
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
