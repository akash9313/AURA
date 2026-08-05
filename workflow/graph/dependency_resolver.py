import logging
from typing import Dict, List, Set

from workflow.graph.models import CriticalPath, GraphNode

logger = logging.getLogger("AURA.Workflow.Graph.Resolver")


class DependencyResolver:
    def topological_sort(self, nodes: Dict[str, GraphNode]) -> List[str]:
        in_degree = {nid: 0 for nid in nodes}
        adj_list = {nid: [] for nid in nodes}

        for nid, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id in nodes:
                    in_degree[nid] += 1
                    adj_list[dep_id].append(nid)

        queue = [nid for nid, count in in_degree.items() if count == 0]
        sorted_ids = []

        while queue:
            curr = queue.pop(0)
            sorted_ids.append(curr)

            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(sorted_ids) != len(nodes):
            raise ValueError("Cyclic dependency detected in task graph")

        return sorted_ids

    def calculate_critical_path(self, nodes: Dict[str, GraphNode]) -> CriticalPath:
        sorted_ids = self.topological_sort(nodes)
        earliest_finish = {nid: 0.0 for nid in nodes}
        predecessors = {nid: None for nid in nodes}

        for nid in sorted_ids:
            node = nodes[nid]
            duration = node.estimated_duration
            max_pred_finish = 0.0
            best_pred = None

            for dep_id in node.dependencies:
                if dep_id in earliest_finish and earliest_finish[dep_id] > max_pred_finish:
                    max_pred_finish = earliest_finish[dep_id]
                    best_pred = dep_id

            earliest_finish[nid] = max_pred_finish + duration
            predecessors[nid] = best_pred

        if not sorted_ids:
            return CriticalPath(total_duration=0.0, path_task_ids=[])

        max_nid = max(sorted_ids, key=lambda nid: earliest_finish[nid])
        total_duration = earliest_finish[max_nid]

        path = []
        curr = max_nid
        while curr:
            path.append(curr)
            curr = predecessors[curr]

        path.reverse()
        return CriticalPath(total_duration=total_duration, path_task_ids=path)

    def get_failure_impact(self, failed_node_id: str, nodes: Dict[str, GraphNode]) -> Set[str]:
        adj_list = {nid: [] for nid in nodes}
        for nid, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id in nodes:
                    adj_list[dep_id].append(nid)

        impacted: Set[str] = set()
        queue = [failed_node_id]

        while queue:
            curr = queue.pop(0)
            for child in adj_list.get(curr, []):
                if child not in impacted:
                    impacted.add(child)
                    queue.append(child)

        return impacted
