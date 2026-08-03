import unittest
from workflow.dependency_graph import DependencyGraph
from workflow.engine import WorkflowEngine
from workflow.models import TaskState, TaskType, WorkflowState
from workflow.planner import WorkflowPlanner
from workflow.recovery import WorkflowRecoveryManager
from workflow.task import WorkflowTask
from workflow.validator import WorkflowValidator
from workflow.workflow import Workflow


class TestWorkflowEngine(unittest.TestCase):

    def test_dag_validation_success(self):
        """Test valid DAG topological sorting."""
        t1 = WorkflowTask(task_id="task_1", tool="open_application", description="Start app")
        t2 = WorkflowTask(task_id="task_2", tool="type_text", description="Type text", dependencies={"task_1"})
        t3 = WorkflowTask(task_id="task_3", tool="open_page", description="Browse URL", dependencies={"task_2"})

        wf = Workflow(workflow_id="wf_test_dag", goal="Test DAG")
        wf.add_task(t1)
        wf.add_task(t2)
        wf.add_task(t3)

        graph = DependencyGraph(wf.tasks)
        order = graph.get_topological_order()
        self.assertEqual(order, ["task_1", "task_2", "task_3"])

    def test_dag_cycle_detection(self):
        """Test cyclic dependency detection raises ValueError."""
        t1 = WorkflowTask(task_id="task_a", tool="chat", description="Task A", dependencies={"task_b"})
        t2 = WorkflowTask(task_id="task_b", tool="chat", description="Task B", dependencies={"task_a"})

        wf = Workflow(workflow_id="wf_cycle", goal="Test Cycle")
        wf.add_task(t1)
        wf.add_task(t2)

        graph = DependencyGraph(wf.tasks)
        with self.assertRaises(ValueError):
            graph.validate_dag()

    def test_workflow_planner(self):
        """Test WorkflowPlanner goal decomposition."""
        planner = WorkflowPlanner()
        wf = planner.plan_workflow("Create a React portfolio")
        self.assertEqual(len(wf.tasks), 3)
        self.assertEqual(wf.state, WorkflowState.READY)

    def test_recovery_manager(self):
        """Test task retry and failure handling."""
        recovery = WorkflowRecoveryManager()
        task = WorkflowTask(task_id="t_fail", tool="chat", description="Fail task", max_retries=2)

        # Retry 1
        can_retry1 = recovery.handle_task_failure(task)
        self.assertTrue(can_retry1)
        self.assertEqual(task.state, TaskState.RETRYING)

        # Retry 2
        can_retry2 = recovery.handle_task_failure(task)
        self.assertTrue(can_retry2)

        # Retry 3 -> Exceeded
        can_retry3 = recovery.handle_task_failure(task)
        self.assertFalse(can_retry3)
        self.assertEqual(task.state, TaskState.FAILED)

    def test_workflow_engine_end_to_end(self):
        """Test WorkflowEngine end-to-end mission execution."""
        engine = WorkflowEngine()
        report = engine.run_mission("Research AI startups")

        self.assertEqual(report["status"], "completed")
        self.assertGreater(len(report["completed_tasks"]), 0)


if __name__ == "__main__":
    unittest.main()
