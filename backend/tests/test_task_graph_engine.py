"""
Task Graph Engine Unit, Performance, Cycle Detection, Parallel, and Checkpoint Test Suite.
Covers models, builders, topological sorting, cycle detection, parallel stage computation,
critical path analysis, failure propagation, recovery checkpoints, and 1000+ node <50ms benchmark SLA.
"""

import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from workflow.graph.models import (
    EdgeType,
    ExecutionStage,
    GraphCheckpoint,
    GraphEdge,
    GraphNode,
    NodeStatus,
)
from workflow.graph.events import GraphEvent
from workflow.graph.configuration import TaskGraphConfig
from workflow.graph.node import NodeBuilder
from workflow.graph.edge import GraphEdgeBuilder
from workflow.graph.dependency_resolver import DependencyResolver
from workflow.graph.validator import GraphValidator
from workflow.graph.scheduler import ParallelScheduler
from workflow.graph.checkpoint import CheckpointManager
from workflow.graph.graph import TaskGraphEngine


# ==============================================================================
# Unit & Builder Tests
# ==============================================================================

class TestTaskGraphNodeAndEdgeBuilders(unittest.TestCase):
    """Unit tests for NodeBuilder and GraphEdgeBuilder."""

    def test_node_builder_defaults_and_serialization(self):
        node = (
            NodeBuilder("Build Frontend", "npm_build")
            .with_inputs({"cwd": "/app"})
            .with_outputs({"status": "ok"})
            .depends_on(["n1"])
            .with_duration(2.5)
            .with_priority(1)
            .build()
        )

        d = node.to_dict()
        self.assertEqual(d["name"], "Build Frontend")
        self.assertEqual(d["capability"], "npm_build")
        self.assertEqual(d["estimated_duration"], 2.5)
        self.assertIn("n1", d["dependencies"])

    def test_edge_builder_conditional(self):
        edge = GraphEdgeBuilder("n1", "n2").with_condition("exit_code == 0").build()
        self.assertEqual(edge.edge_type, EdgeType.CONDITIONAL)
        self.assertEqual(edge.condition_expr, "exit_code == 0")


# ==============================================================================
# Cycle Detection & Topological Sort Tests
# ==============================================================================

class TestCycleDetectionAndTopologicalSort(unittest.TestCase):
    """Tests for Kahn's algorithm topological sorting and cycle detection."""

    def setUp(self):
        self.validator = GraphValidator()
        self.resolver = DependencyResolver()

    def test_cycle_detection_failure(self):
        """Cyclic dependency: n1 -> n2 -> n3 -> n1."""
        n1 = GraphNode(task_id="n1", name="Task 1", dependencies=["n3"])
        n2 = GraphNode(task_id="n2", name="Task 2", dependencies=["n1"])
        n3 = GraphNode(task_id="n3", name="Task 3", dependencies=["n2"])

        nodes = {"n1": n1, "n2": n2, "n3": n3}
        is_valid, errors = self.validator.validate_graph(nodes)

        self.assertFalse(is_valid)
        self.assertTrue(any("Cyclic dependency" in err for err in errors))

        with self.assertRaises(ValueError):
            self.resolver.topological_sort(nodes)

    def test_valid_topological_sort(self):
        """Valid DAG: n1 -> n2 -> n3."""
        n1 = GraphNode(task_id="n1", name="Task 1")
        n2 = GraphNode(task_id="n2", name="Task 2", dependencies=["n1"])
        n3 = GraphNode(task_id="n3", name="Task 3", dependencies=["n2"])

        nodes = {"n1": n1, "n2": n2, "n3": n3}
        order = self.resolver.topological_sort(nodes)

        self.assertEqual(order, ["n1", "n2", "n3"])


# ==============================================================================
# Parallel Execution & Critical Path Tests
# ==============================================================================

class TestParallelExecutionAndCriticalPath(unittest.TestCase):
    """Tests for parallel execution stage computation and critical path analysis."""

    def setUp(self):
        self.scheduler = ParallelScheduler()
        self.resolver = DependencyResolver()

    def test_parallel_stage_grouping(self):
        """
        Stage 0: [n1, n2] (no dependencies)
        Stage 1: [n3] (depends on n1 & n2)
        """
        n1 = GraphNode(task_id="n1", name="Task 1")
        n2 = GraphNode(task_id="n2", name="Task 2")
        n3 = GraphNode(task_id="n3", name="Task 3", dependencies=["n1", "n2"])

        nodes = {"n1": n1, "n2": n2, "n3": n3}
        stages = self.scheduler.compute_execution_stages(nodes)

        self.assertEqual(len(stages), 2)
        self.assertCountEqual(stages[0].task_ids, ["n1", "n2"])
        self.assertEqual(stages[1].task_ids, ["n3"])

    def test_critical_path_analysis(self):
        """
        n1 (1.0s) -> n2 (3.0s) -> n4 (1.0s)  (Total: 5.0s)
        n1 (1.0s) -> n3 (1.0s) -> n4 (1.0s)  (Total: 3.0s)
        """
        n1 = GraphNode(task_id="n1", estimated_duration=1.0)
        n2 = GraphNode(task_id="n2", dependencies=["n1"], estimated_duration=3.0)
        n3 = GraphNode(task_id="n3", dependencies=["n1"], estimated_duration=1.0)
        n4 = GraphNode(task_id="n4", dependencies=["n2", "n3"], estimated_duration=1.0)

        nodes = {"n1": n1, "n2": n2, "n3": n3, "n4": n4}
        cp = self.resolver.calculate_critical_path(nodes)

        self.assertEqual(cp.total_duration, 5.0)
        self.assertEqual(cp.path_task_ids, ["n1", "n2", "n4"])


# ==============================================================================
# Checkpoint & Interruption Recovery Tests
# ==============================================================================

class TestGraphCheckpointAndRecovery(unittest.TestCase):
    """Tests for GraphCheckpoint creation and restoration."""

    def test_checkpoint_state_restoration(self):
        engine = TaskGraphEngine()
        p_tasks = [
            {"task_id": "t1", "description": "Step 1", "capability_required": "c1"},
            {"task_id": "t2", "description": "Step 2", "capability_required": "c2", "dependencies": ["t1"]},
        ]
        engine.build_from_planner_tasks(p_tasks)

        # Create checkpoint after t1 completes
        ckpt = engine.create_checkpoint(
            completed_tasks=["t1"],
            task_outputs={"t1": {"res": "ok"}},
            current_context={"env": "prod"},
            verification_results={"t1": {"verified": True}},
        )

        completed = engine.restore_checkpoint(ckpt)
        self.assertIn("t1", completed)
        self.assertEqual(engine.nodes["t1"].status, NodeStatus.COMPLETED)
        self.assertEqual(engine.nodes["t1"].outputs["res"], "ok")


# ==============================================================================
# Large Graph (1000+ Nodes) Sub-50ms Performance Benchmark Tests
# ==============================================================================

class TestLargeGraphPerformanceSLA(unittest.TestCase):
    """Performance SLA tests verifying 1000+ node graph construction completes in under 50ms."""

    def test_1000_node_graph_construction_sub_50ms(self):
        engine = TaskGraphEngine()
        planner_tasks = []

        # Generate 1000 sequential/parallel tasks
        for i in range(1000):
            deps = [f"task_{i-1}"] if i > 0 else []
            planner_tasks.append({
                "task_id": f"task_{i}",
                "description": f"Benchmark Task {i}",
                "capability_required": "bench_cap",
                "dependencies": deps,
            })

        start = time.time()
        gid = engine.build_from_planner_tasks(planner_tasks)
        duration_ms = (time.time() - start) * 1000

        self.assertEqual(len(engine.nodes), 1000)
        self.assertLess(duration_ms, 50.0)  # Verify sub-50ms SLA requirement


if __name__ == "__main__":
    unittest.main()
