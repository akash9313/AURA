"""
Workflow Executor Integration Unit, Parallel Execution, Recovery, Verification, and Cancellation Test Suite.
Tests CapabilityDispatcher, ExecutionCoordinator, ProgressReporter, ResultFormatter, and WorkflowExecutorIntegrationService.
"""

import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, ".")

from workflow.integration.models import (
    MissionExecutionResult,
    MissionExecutionStatus,
    TaskExecutionProgress,
)
from workflow.integration.events import WorkflowIntegrationEvent
from workflow.integration.configuration import WorkflowIntegrationConfig
from workflow.integration.capability_dispatcher import (
    CapabilityDispatcher,
    CapabilityNotFoundError,
    VerificationFailedError,
)
from workflow.integration.progress_reporter import ProgressReporter
from workflow.integration.result_formatter import ResultFormatter
from workflow.integration.execution_coordinator import ExecutionCoordinator
from workflow.integration.executor_service import WorkflowExecutorIntegrationService
from planner.models import PlannerTask, TaskGraph


class TestWorkflowIntegration(unittest.TestCase):
    """Test suite for Workflow Executor Integration subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = WorkflowIntegrationConfig(
            max_execution_time_sec=5.0,
            parallel_task_limit=2,
            max_retries=2,
            backoff_sec=0.01,
        )
        self.reporter = ProgressReporter(bus=self.bus)
        self.formatter = ResultFormatter()

    def test_capability_dispatcher_mandatory_registry_check(self):
        """Test CapabilityDispatcher raises CapabilityNotFoundError when capability missing from Registry."""
        mock_cap_service = MagicMock()
        mock_cap_service.get_capability.return_value = None
        mock_cap_service.find_best_capability.return_value = None

        dispatcher = CapabilityDispatcher(capability_service=mock_cap_service)

        with self.assertRaises(CapabilityNotFoundError):
            asyncio.run(dispatcher.dispatch_and_verify_task("t1", "unregistered_cap", {}))

    def test_capability_dispatcher_mandatory_verification(self):
        """Test CapabilityDispatcher enforces empirical goal verification before task completion."""
        mock_cap_service = MagicMock()
        mock_cap = MagicMock()
        mock_cap.name = "test_cap"
        mock_cap.category.value = "system"
        mock_cap_service.get_capability.return_value = mock_cap

        mock_verif_service = MagicMock()
        mock_verif_result = MagicMock()
        mock_verif_result.verified = False
        mock_verif_result.summary = "Screen state did not change"
        mock_verif_service.verify_goal = AsyncMock(return_value=mock_verif_result)

        dispatcher = CapabilityDispatcher(
            capability_service=mock_cap_service,
            verification_service=mock_verif_service,
        )

        with self.assertRaises(VerificationFailedError):
            asyncio.run(dispatcher.dispatch_and_verify_task("t1", "test_cap", {}))

    def test_parallel_execution_and_progress_events(self):
        """Test ExecutionCoordinator parallel task execution and progress event publishing."""
        graph = TaskGraph()
        t1 = PlannerTask(task_id="t1", description="Task 1", capability_required="cap1")
        t2 = PlannerTask(task_id="t2", description="Task 2", capability_required="cap2")
        graph.add_task(t1)
        graph.add_task(t2)

        mock_dispatcher = MagicMock()
        mock_dispatcher.dispatch_and_verify_task = AsyncMock(return_value={
            "task_id": "t",
            "capability": "cap",
            "verification": {"verified": True},
            "duration_sec": 0.01,
        })

        coordinator = ExecutionCoordinator(
            config=self.config,
            dispatcher=mock_dispatcher,
            reporter=self.reporter,
        )

        res = asyncio.run(coordinator.execute_mission_plan("msn_123", graph))

        self.assertEqual(res.status, MissionExecutionStatus.COMPLETED)
        self.assertEqual(len(res.completed_tasks), 2)

        # Verify EventBus events published
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_started", published)
        self.assertIn("task_started", published)
        self.assertIn("task_completed", published)
        self.assertIn("mission_completed", published)

    def test_recovery_attempts(self):
        """Test task retry and recovery attempt counting on transient failure."""
        graph = TaskGraph()
        t1 = PlannerTask(task_id="t1", description="Task 1", capability_required="cap1")
        graph.add_task(t1)

        mock_dispatcher = MagicMock()
        # Fail first attempt, succeed second attempt
        mock_dispatcher.dispatch_and_verify_task = AsyncMock(side_effect=[
            VerificationFailedError("Transient failure"),
            {"task_id": "t1", "capability": "cap1", "verification": {"verified": True}, "duration_sec": 0.01},
        ])

        coordinator = ExecutionCoordinator(
            config=self.config,
            dispatcher=mock_dispatcher,
            reporter=self.reporter,
        )

        res = asyncio.run(coordinator.execute_mission_plan("msn_retry", graph))
        self.assertEqual(res.status, MissionExecutionStatus.COMPLETED)
        self.assertEqual(res.recovery_attempts, 1)

    def test_cancellation(self):
        """Test mission cancellation via CancellationToken."""
        graph = TaskGraph()
        t1 = PlannerTask(task_id="t1", description="Task 1", capability_required="cap1")
        graph.add_task(t1)

        mock_dispatcher = MagicMock()
        coordinator = ExecutionCoordinator(
            config=self.config,
            dispatcher=mock_dispatcher,
            reporter=self.reporter,
        )

        coordinator.cancel("User aborted operation")
        res = asyncio.run(coordinator.execute_mission_plan("msn_cancel", graph))

        self.assertEqual(res.status, MissionExecutionStatus.CANCELLED)

        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_cancelled", published)


if __name__ == "__main__":
    unittest.main()
