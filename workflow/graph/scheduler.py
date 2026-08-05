import logging
from typing import Dict, List, Set

from workflow.graph.models import ExecutionStage, GraphNode, NodeStatus

logger = logging.getLogger("AURA.Workflow.Graph.Scheduler")


class ParallelScheduler:
    def compute_execution_stages(self, nodes: Dict[str, GraphNode]) -> List[ExecutionStage]:
        in_degree = {nid: 0 for nid in nodes}
        adj_list = {nid: [] for nid in nodes}

        for nid, node in nodes.items():
            for dep_id in node.dependencies:
                if dep_id in nodes:
                    in_degree[nid] += 1
                    adj_list[dep_id].append(nid)

        current_stage_nodes = [nid for nid, count in in_degree.items() if count == 0]
        stages: List[ExecutionStage] = []
        stage_idx = 0

        processed_count = 0

        while current_stage_nodes:
            stages.append(ExecutionStage(stage_index=stage_idx, task_ids=current_stage_nodes))
            processed_count += len(current_stage_nodes)
            next_stage_nodes = []

            for nid in current_stage_nodes:
                for neighbor in adj_list[nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_stage_nodes.append(neighbor)

            current_stage_nodes = next_stage_nodes
            stage_idx += 1

        if processed_count != len(nodes):
            raise ValueError("Cyclic dependency detected in task graph")

        return stages

    def get_ready_nodes(self, nodes: Dict[str, GraphNode], completed_node_ids: Set[str]) -> List[str]:
        ready = []
        for nid, node in nodes.items():
            if node.status in (NodeStatus.PENDING, NodeStatus.READY):
                if all(dep_id in completed_node_ids for dep_id in node.dependencies):
                    ready.append(nid)
        return ready
