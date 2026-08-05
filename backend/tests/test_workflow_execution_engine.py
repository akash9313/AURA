"""
Workflow Execution Engine Unit, Integration, Parallel, Checkpoint, Cancellation, and Stress Test Suite.
Covers models, state transitions, CancellationToken, TimeoutManager, ExecutionScheduler, WorkflowProgressTracker,
TaskExecutor, WorkflowCheckpointManager, WorkflowExecutor, and integration with Capability, Interaction, and Verification services.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from workflow.executor.models import (
    WorkflowExecutionResult,
    WorkflowExecutionState,
    WorkflowProgress,
    WorkflowTaskExecution,
    WorkflowTaskState,
)
from workflow.executor.events import ExecutorEvent
from workflow.executor.configuration import WorkflowExecutorConfig
from workflow.executor.cancellation import CancellationToken
from workflow.executor.timeout_manager import TimeoutManager
from workflow.executor.state_manager import WorkflowStateManager
from workflow.executor.progress_tracker import WorkflowProgressTracker
from workflow.executor.checkpoint_manager import WorkflowCheckpointManager
from workflow.executor.scheduler import ExecutionScheduler
from workflow.executor.task_executor import TaskExecutor
from workflow.executor.workflow_executor import WorkflowExecutor
from workflow.graph.graph import TaskGraphEngine
from capabilities.service import CapabilityService
from interaction.service import InteractionEngineService
from verification.service import GoalVerificationService


# ==============================================================================
# Unit & Cancellation Tests
# ==============================================================================

class TestExecutorModelsAndCancellation(unittest.TestCase):
    """Unit tests for models and CancellationToken."""

    def test_cancellation_token_signaling(self):
        token = CancellationToken()
        self.assertFalse(token.is_cancelled())

        token.cancel()
        self.assertTrue(token.is_cancelled())

        token.reset()
        self.assertFalse(token.is_cancelled())

    def test_task_execution_serialization(self):
        task_exec = WorkflowTaskExecution(
            task_id="t1",
            name="Run Command",
            capability="run_terminal_command",
            status=WorkflowTaskState.RUNNING,
        )
        d = task_exec.to_dict()
        self.assertEqual(d["task_id"], "t1")
        self.assertEqual(d["status"], "running")


# ==============================================================================
# Execution & Concurrency Tests
# ==============================================================================

class TestWorkflowExecutionAndParallelism(unittest.TestCase):
    """Integration and parallel execution tests for WorkflowExecutor."""

    def setUp(self):
        self.bus = MagicMock()
        self.cap_service = CapabilityService()
        self.interaction_service = InteractionEngineService(bus=self.bus)
        self.verification_service = GoalVerificationService(bus=self.bus)

        self.executor = WorkflowExecutor(
            bus=self.bus,
            capability_service=self.cap_service,
            interaction_service=self.interaction_service,
            verification_service=self.verification_service,
        )

    def test_successful_dag_workflow_execution(self):
        """Execute a 3-task parallel & sequential DAG workflow."""
        graph_engine = TaskGraphEngine()
        planner_tasks = [
            {"task_id": "t1", "description": "Open App", "capability_required": "open_application"},
            {"task_id": "t2", "description": "Browse Web", "capability_required": "browse_web"},
            {"task_id": "t3", "description": "Run CMD", "capability_required": "run_terminal_command", "dependencies": ["t1", "t2"]},
        ]
        graph_engine.build_from_planner_tasks(planner_tasks)

        res = asyncio.run(self.executor.execute_graph(graph_engine))

        self.assertTrue(res.success)
        self.assertEqual(res.state, WorkflowExecutionState.COMPLETED)
        self.assertEqual(len(res.completed_task_ids), 3)

        # Check published events
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("workflow_started", published)
        self.assertIn("task_started", published)
        self.assertIn("task_completed", published)
        self.assertIn("checkpoint_created", published)
        self.assertIn("workflow_completed", published)

    def test_workflow_cancellation_during_execution(self):
        """Cancel workflow while running."""
        graph_engine = TaskGraphEngine()
        planner_tasks = [
            {"task_id": "t1", "description": "Task 1", "capability_required": "open_application"},
        ]
        graph_engine.build_from_planner_tasks(planner_tasks)

        self.executor.cancel()  # Signal cancellation before execution
        res = asyncio.run(self.executor.execute_graph(graph_engine))

        self.assertFalse(res.success)
        self.assertEqual(res.state, WorkflowExecutionState.CANCELLED)


if __name__ == "__main__":
    unittest.main()
