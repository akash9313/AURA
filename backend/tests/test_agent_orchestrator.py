import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from agent.orchestrator import AgentOrchestrator
from agent.state import TaskStatus, WorkflowState
from agent.task import Task
from memory.manager import MemoryManager
from memory.persistence import SQLiteDatabase
from memory.store import SQLiteMemoryRepository
from tools.registry import ToolRegistry


class TestAgentOrchestrator(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for memory persistence during testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        self.db = SQLiteDatabase(db_path=self.temp_db.name)
        self.repo = SQLiteMemoryRepository(db=self.db)
        self.memory = MemoryManager(repo=self.repo)

        self.registry = ToolRegistry(auto_discover=True)
        self.orchestrator = AgentOrchestrator(
            registry=self.registry,
            memory=self.memory
        )

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    @patch("subprocess.Popen")
    def test_scenario_1_single_task_open_notepad(self, mock_popen):
        """Scenario 1: User says 'Open Notepad'."""
        goal = "Open Notepad"
        workflow = self.orchestrator.process_goal(goal)

        self.assertEqual(workflow.status, WorkflowState.COMPLETED)
        self.assertEqual(len(workflow.tasks), 1)
        self.assertEqual(workflow.tasks[0].status, TaskStatus.COMPLETED)
        mock_popen.assert_called_once_with("notepad.exe")

    @patch("subprocess.Popen")
    def test_scenario_2_multi_task_open_chrome_and_calculator(self, mock_popen):
        """Scenario 2: User says 'Open Chrome and Calculator'."""
        goal = "Open Chrome and Calculator"
        workflow = self.orchestrator.process_goal(goal)

        self.assertEqual(workflow.status, WorkflowState.COMPLETED)
        self.assertGreaterEqual(len(workflow.tasks), 2)
        for t in workflow.tasks:
            self.assertEqual(t.status, TaskStatus.COMPLETED)
        self.assertGreaterEqual(mock_popen.call_count, 2)

    @patch("ai.llm.ask_ai", return_value="Mocked document summary")
    def test_scenario_3_pdf_document_summarization_workflow(self, mock_ask_ai):
        """Scenario 3: User says 'Read a PDF and summarize it'."""
        goal = "Read a PDF and summarize it"
        workflow = self.orchestrator.process_goal(goal)

        self.assertEqual(workflow.status, WorkflowState.COMPLETED)
        self.assertEqual(len(workflow.tasks), 2)
        # Check task dependencies
        t1, t2 = workflow.tasks[0], workflow.tasks[1]
        self.assertEqual(t1.tool_name, "read_document")
        self.assertEqual(t2.tool_name, "chat")
        self.assertIn(t1.task_id, t2.dependencies)

    def test_task_validation_and_retry(self):
        """Test task validator and retry strategy for non-existent tools."""
        # Create custom workflow with an unregistered tool
        from agent.workflow import Workflow
        wf = Workflow(goal="Execute unregistered tool")
        t = Task(tool_name="unregistered_non_existent_tool_xyz", parameters={})
        wf.tasks.append(t)

        with patch.object(self.orchestrator.planner, "plan_goal", return_value=wf):
            res_wf = self.orchestrator.process_goal("Execute unregistered tool")
            self.assertEqual(res_wf.status, WorkflowState.FAILED)
            self.assertEqual(res_wf.tasks[0].status, TaskStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
