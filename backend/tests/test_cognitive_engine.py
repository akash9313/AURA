import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from agent.state import TaskStatus, WorkflowState
from cognition.confidence import ConfidenceEngine
from cognition.decision import DecisionEngine

from cognition.engine import CognitiveEngine
from cognition.evaluator import PlanEvaluator
from cognition.goal_manager import GoalManager, GoalStatus, GoalType
from cognition.models import CognitiveDecision, GoalStatus, RiskLevel
from cognition.reflection import ReflectionEngine
from cognition.state import CognitiveStateManager
from memory.manager import MemoryManager
from memory.persistence import SQLiteDatabase
from memory.store import SQLiteMemoryRepository
from tools.registry import ToolRegistry


class TestCognitiveEngine(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for memory persistence during testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        self.db = SQLiteDatabase(db_path=self.temp_db.name)
        self.repo = SQLiteMemoryRepository(db=self.db)
        self.memory = MemoryManager(repo=self.repo)

        self.registry = ToolRegistry(auto_discover=True)
        self.engine = CognitiveEngine(
            registry=self.registry,
            memory=self.memory
        )

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    @patch("subprocess.Popen")
    def test_full_cognitive_loop_desktop_action(self, mock_popen):
        """Test full 8-stage cognitive loop for desktop automation request."""
        res = self.engine.process_request("Open Notepad")

        self.assertIn("answer", res)
        self.assertEqual(res["goal"]["status"], GoalStatus.COMPLETED.value)
        self.assertEqual(res["confidence"]["risk_level"], RiskLevel.LOW.value)
        self.assertTrue(res["reflection"]["was_successful"])
        mock_popen.assert_called_once_with("notepad.exe")

    def test_decision_engine_capability_routing(self):
        """Test DecisionEngine capability selection for different intent categories."""
        decision_engine = DecisionEngine()

        # Web Strategy
        dec_web = decision_engine.decide_strategy("Search web for Python AI news")
        self.assertTrue(dec_web.needs_browser)

        # Vision Strategy
        dec_vision = decision_engine.decide_strategy("Check the screenshot of the screen")
        self.assertTrue(dec_vision.needs_vision)

        # Desktop Strategy
        dec_desktop = decision_engine.decide_strategy("Open Calculator")
        self.assertTrue(dec_desktop.needs_tools)

        # Direct Answer Strategy
        dec_direct = decision_engine.decide_strategy("What is artificial intelligence?")
        self.assertTrue(dec_direct.needs_direct_answer)

    def test_goal_manager_lifecycle(self):
        """Test GoalManager creation, dependency tracking, and status transitions."""
        gm = GoalManager()
        g1 = gm.create_goal("Task 1", goal_type=GoalType.SHORT_TERM)
        g2 = gm.create_goal("Task 2", goal_type=GoalType.DEPENDENT, dependencies=[g1.goal_id])

        self.assertEqual(g1.status, GoalStatus.PENDING)
        gm.update_status(g1.goal_id, GoalStatus.COMPLETED)
        self.assertEqual(gm.get_goal(g1.goal_id).status, GoalStatus.COMPLETED)

    def test_confidence_and_evaluator(self):
        """Test ConfidenceEngine and PlanEvaluator risk scoring."""
        conf_engine = ConfidenceEngine()
        score_low = conf_engine.evaluate_task_risk("open_application", {"application": "notepad"})
        self.assertEqual(score_low.risk_level, RiskLevel.LOW)

        score_high = conf_engine.evaluate_task_risk("delete_database", {})
        self.assertEqual(score_high.risk_level, RiskLevel.HIGH)

    def test_reflection_and_memory_persistence(self):
        """Test ReflectionEngine analysis and memory learning persistence."""
        from agent.workflow import Workflow
        wf = Workflow(goal="Test Reflection Goal")
        wf.status = WorkflowState.COMPLETED


        reflection_engine = ReflectionEngine(memory=self.memory)
        rec = reflection_engine.reflect_on_workflow(wf)
        self.assertTrue(rec.was_successful)
        self.assertIn("Test Reflection Goal", rec.summary)


if __name__ == "__main__":
    unittest.main()
