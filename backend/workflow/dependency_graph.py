import collections
import logging
from typing import Dict, List, Set
from workflow.task import WorkflowTask

logger = logging.getLogger("AURA.Workflow.DependencyGraph")


class DependencyGraph:
    """
    Manages Directed Acyclic Graph (DAG) validation and topological sorting for tasks.
    """

    def __init__(self, tasks: Dict[str, WorkflowTask]):
        self.tasks = tasks

    def validate_dag(self) -> bool:
        """
        Validate if task graph forms a valid DAG without cycles.

        Returns:
            bool: True if DAG is valid, raises ValueError if cycle is detected.
        """
        in_degree = {task_id: 0 for task_id in self.tasks}
        graph = collections.defaultdict(list)

        for task_id, task in self.tasks.items():
            for parent_id in task.dependencies:
                if parent_id in self.tasks:
                    graph[parent_id].append(task_id)
                    in_degree[task_id] += 1

        queue = collections.deque([t for t, count in in_degree.items() if count == 0])
        visited_count = 0

        while queue:
            node = queue.popleft()
            visited_count += 1
            for child in graph[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if visited_count != len(self.tasks):
            logger.error("Cyclic dependency detected in workflow task DAG graph!")
            raise ValueError("Workflow task graph contains cyclic dependencies.")

        return True

    def get_topological_order(self) -> List[str]:

        """Return topological order of task execution IDs."""
        self.validate_dag()
        in_degree = {task_id: 0 for task_id in self.tasks}
        graph = collections.defaultdict(list)

        for task_id, task in self.tasks.items():
            for parent_id in task.dependencies:
                if parent_id in self.tasks:
                    graph[parent_id].append(task_id)
                    in_degree[task_id] += 1

        queue = collections.deque([t for t, count in in_degree.items() if count == 0])
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for child in graph[node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return order
