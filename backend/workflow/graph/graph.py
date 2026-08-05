"""
Production-Grade Task Graph Engine Master Controller.
Converts Planner output into dependency-aware Directed Acyclic Graphs (DAG).
Handles dependency resolution, parallel scheduling, critical path analysis, failure propagation, and checkpoints.
Must NEVER execute tasks directly.
"""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Set

from workflow.graph.checkpoint import CheckpointManager
from workflow.graph.configuration import TaskGraphConfig
from workflow.graph.dependency_resolver import DependencyResolver
from workflow.graph.edge import GraphEdgeBuilder
from workflow.graph.events import GraphEvent
from workflow.graph.models import (
    CriticalPath,
    EdgeType,
    ExecutionStage,
    GraphCheckpoint,
    GraphEdge,
    GraphNode,
    NodeStatus,
)
from workflow.graph.node import NodeBuilder
from workflow.graph.scheduler import ParallelScheduler
from workflow.graph.validator import GraphValidator

logger = logging.getLogger("AURA.Workflow.Graph.Engine")


class TaskGraphEngine:
    """
    Task Graph Engine Master Controller.
    Strictly manages DAG construction, dependency resolution, parallel scheduling, and checkpoints without executing tasks.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[TaskGraphConfig] = None,
    ):
        self.bus = bus
        self.config = config or TaskGraphConfig()

        self.graph_id: str = f"graph_{uuid.uuid4().hex[:8]}"
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

        self.resolver = DependencyResolver()
        self.scheduler = ParallelScheduler()
        self.validator = GraphValidator()
        self.checkpoint_manager = CheckpointManager()

        logger.info(f"TaskGraphEngine initialized for graph '{self.graph_id}'")

    def build_from_planner_tasks(self, planner_tasks: List[Any]) -> str:
        """
        Convert list of PlannerTask items into DAG GraphNode and GraphEdge instances.
        Enforces sub-50ms SLA performance for normal workflows.

        Args:
            planner_tasks: List of PlannerTask objects (or dictionaries).

        Returns:
            graph_id string.
        """
        start_time = time.time()
        logger.info(f"Building Task Graph from {len(planner_tasks)} planner tasks...")

        self.nodes.clear()
        self.edges.clear()

        # 1. Convert planner tasks into GraphNodes
        for ptask in planner_tasks:
            tid = getattr(ptask, "task_id", None) or ptask.get("task_id")
            desc = getattr(ptask, "description", "") or ptask.get("description", "")
            cap = getattr(ptask, "capability_required", "") or ptask.get("capability_required", "")
            inputs = getattr(ptask, "inputs", {}) or ptask.get("inputs", {})
            outputs = getattr(ptask, "outputs", {}) or ptask.get("outputs", {})
            deps = getattr(ptask, "dependencies", []) or ptask.get("dependencies", [])
            vrule = getattr(ptask, "verification_rule", {}) or ptask.get("verification_rule", {})
            rpolicy = getattr(ptask, "retry_policy", {}) or ptask.get("retry_policy", {})

            node = (
                NodeBuilder(name=desc, capability=cap, task_id=tid)
                .with_inputs(inputs)
                .with_outputs(outputs)
                .depends_on(deps)
                .with_verification(vrule)
                .build()
            )
            node.retry_policy = rpolicy
            self.nodes[node.task_id] = node

            # Build edges for dependencies
            for dep_id in deps:
                edge = GraphEdgeBuilder(source_id=dep_id, target_id=node.task_id).with_type(EdgeType.HARD).build()
                self.edges.append(edge)

        # 2. Validate DAG
        is_valid, errors = self.validator.validate_graph(self.nodes)
        if not is_valid:
            msg = f"Graph validation failed: {errors}"
            logger.error(msg)
            self._publish_event(GraphEvent.GRAPH_FAILED, {"error": msg})
            raise ValueError(msg)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Task Graph '{self.graph_id}' built and validated in {round(duration_ms, 2)}ms (Target: <50ms)")
        self._publish_event(GraphEvent.GRAPH_CREATED, {"graph_id": self.graph_id, "node_count": len(self.nodes)})
        self._publish_event(GraphEvent.GRAPH_VALIDATED, {"graph_id": self.graph_id})

        return self.graph_id

    def get_topological_order(self) -> List[str]:
        """Get topological ordering of task IDs."""
        return self.resolver.topological_sort(self.nodes)

    def get_parallel_execution_stages(self) -> List[ExecutionStage]:
        """Get parallel execution stage batching."""
        return self.scheduler.compute_execution_stages(self.nodes)

    def get_critical_path(self) -> CriticalPath:
        """Calculate critical path through graph."""
        return self.resolver.calculate_critical_path(self.nodes)

    def get_failure_impact(self, failed_task_id: str) -> Set[str]:
        """Get all downstream task IDs affected if failed_task_id fails."""
        return self.resolver.get_failure_impact(failed_task_id, self.nodes)

    def create_checkpoint(
        self,
        completed_tasks: List[str],
        task_outputs: Dict[str, Dict[str, Any]],
        current_context: Dict[str, Any],
        verification_results: Dict[str, Dict[str, Any]],
    ) -> GraphCheckpoint:
        """Create recovery checkpoint."""
        ckpt = self.checkpoint_manager.create_checkpoint(
            graph_id=self.graph_id,
            completed_tasks=completed_tasks,
            task_outputs=task_outputs,
            current_context=current_context,
            verification_results=verification_results,
        )
        self._publish_event(GraphEvent.CHECKPOINT_CREATED, ckpt.to_dict())
        return ckpt

    def restore_checkpoint(self, checkpoint: GraphCheckpoint) -> Set[str]:
        """Restore graph state from checkpoint."""
        return self.checkpoint_manager.restore_graph_state(self.nodes, checkpoint)

    def _publish_event(self, event: GraphEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish graph event '{event.value}': {e}")
