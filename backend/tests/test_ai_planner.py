"""
AI Planner Engine Unit & Integration Tests.
Covers PlannerTask models, TaskBuilder, TaskGraph DAG builder, cycle detection,
decomposer (React project creation scenario), plan validator, recovery point tagging,
and AIPlannerService integration.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from planner.models import (
    MissionPlan,
    PlannerTask,
    PlanningContext,
    PlanningResult,
    TaskGraph,
)
from planner.events import PlannerEvent
from planner.configuration import PlannerConfig
from planner.task import TaskBuilder
from planner.graph import TaskGraphBuilder
from planner.decomposer import TaskDecomposer
from planner.validator import PlanValidator
from planner.recovery_points import RecoveryPointManager
from planner.planner import AIPlanner
from planner.service import AIPlannerService


# ==============================================================================
# Domain Models & Task Builder Tests
# ==============================================================================

class TestPlannerModelsAndBuilder(unittest.TestCase):
    """Tests for Planner domain models and TaskBuilder."""

    def test_task_builder_serialization(self):
        task = (
            TaskBuilder("Open Terminal", "launch_app")
            .with_inputs({"executable": "cmd.exe"})
            .with_outputs({"app_id": "term_1"})
            .with_verification({"app_name": "cmd.exe", "status": "running"})
            .mark_recovery_point(True)
            .build()
        )

        d = task.to_dict()
        self.assertEqual(d["description"], "Open Terminal")
        self.assertEqual(d["capability_required"], "launch_app")
        self.assertTrue(d["is_recovery_point"])

    def test_dag_cycle_detection(self):
        builder = TaskGraphBuilder()
        t1 = PlannerTask(task_id="t1", description="Task 1", capability_required="cap1")
        t2 = PlannerTask(task_id="t2", description="Task 2", capability_required="cap2", dependencies=["t1"])
        t1.dependencies = ["t2"]  # Create cycle

        with self.assertRaises(ValueError):
            builder.build_graph([t1, t2])


# ==============================================================================
# Decomposer & Real-World React Scenario Tests
# ==============================================================================

class TestDecomposerAndScenarios(unittest.TestCase):
    """Tests for TaskDecomposer natural language request decomposition."""

    def setUp(self):
        self.decomposer = TaskDecomposer()

    def test_react_project_decomposition_scenario(self):
        """Input: 'Create a React project.' -> Open Terminal -> npm create -> Wait -> Verify -> Open VS Code."""
        ctx = PlanningContext(user_request="Create a React project.")
        tasks = self.decomposer.decompose(ctx)

        self.assertEqual(len(tasks), 5)
        descriptions = [t.description for t in tasks]

        self.assertIn("Open Terminal", descriptions[0])
        self.assertIn("Run npm create react app", descriptions[1])
        self.assertIn("Wait for completion", descriptions[2])
        self.assertIn("Verify project exists", descriptions[3])
        self.assertIn("Open VS Code", descriptions[4])

        # Verify dependency chain
        self.assertIn(tasks[0].task_id, tasks[1].dependencies)
        self.assertIn(tasks[1].task_id, tasks[2].dependencies)


# ==============================================================================
# Planner & Service Integration Tests
# ==============================================================================

class TestAIPlannerServiceIntegration(unittest.TestCase):
    """Integration tests for AIPlannerService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = AIPlannerService(bus=self.bus)

    def test_create_plan_without_execution(self):
        """Planner must generate execution plan without running any actions."""
        res = asyncio.run(self.service.create_plan(user_request="Create a React project."))

        self.assertTrue(res.success)
        self.assertIsNotNone(res.plan)
        self.assertEqual(len(res.plan.task_graph.tasks), 5)
        self.assertGreater(len(res.plan.recovery_points), 0)

        # Verify EVENT_MISSION_STARTED and EVENT_PLAN_CREATED published
        published_events = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_started", published_events)
        self.assertIn("plan_created", published_events)


if __name__ == "__main__":
    unittest.main()
