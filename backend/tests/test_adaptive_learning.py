import unittest
from learning.behavior import BehaviorAdapter
from learning.confidence import ConfidenceModel
from learning.engine import AdaptiveIntelligenceEngine
from learning.models import RiskLevel
from learning.optimizer import WorkflowOptimizer
from learning.preferences import PreferenceEngine
from learning.ranking import ToolRankingEngine
from learning.recommendations import RecommendationEngine
from learning.workflow_learning import WorkflowLearningEngine


class TestAdaptiveLearning(unittest.TestCase):

    def test_preference_engine_defaults_and_infer(self):
        """Test default preferences, custom preference setting, and inference."""
        prefs = PreferenceEngine()
        p_browser = prefs.get_preference("preferred_browser")
        self.assertEqual(p_browser.value, "chrome")

        prefs.infer_preference_from_action("open_app", "Microsoft Edge")
        p_edge = prefs.get_preference("preferred_browser")
        self.assertEqual(p_edge.value, "edge")
        self.assertEqual(p_edge.source, "inferred")

    def test_behavior_adapter(self):
        """Test behavioral overrides using active user preferences."""
        prefs = PreferenceEngine()
        prefs.set_preference("preferred_browser", "edge")
        adapter = BehaviorAdapter(prefs)

        params = {"browser": "default", "url": "https://example.com"}
        updated = adapter.apply_behavioral_overrides(params)
        self.assertEqual(updated["browser"], "edge")

    def test_workflow_learning_and_optimizer(self):
        """Test pattern learning over repeated workflow runs."""
        learning = WorkflowLearningEngine()
        optimizer = WorkflowOptimizer(learning)

        goal = "Research AI startups"
        seq = ["open_page", "page_extract"]

        # Run 1 & 2 success
        learning.record_workflow_execution(goal, seq, success=True)
        learning.record_workflow_execution(goal, seq, success=True)

        opt_seq = optimizer.optimize_sequence(goal, ["open_page", "chat"])
        self.assertEqual(opt_seq, seq)

    def test_confidence_model(self):
        """Test transparent confidence score and risk level calculation."""
        conf = ConfidenceModel()
        rating1 = conf.calculate_confidence(0, 0)
        self.assertEqual(rating1.score, 0.5)

        rating2 = conf.calculate_confidence(9, 10)
        self.assertEqual(rating2.score, 0.9)
        self.assertEqual(rating2.risk_level, RiskLevel.LOW)

    def test_recommendation_engine(self):
        """Test explainable recommendation generation and dismissal."""
        prefs = PreferenceEngine()
        prefs.infer_preference_from_action("open_app", "Microsoft Edge")

        recs = RecommendationEngine(prefs)
        suggested = recs.generate_recommendations()
        self.assertEqual(len(suggested), 1)

        rec_id = suggested[0].recommendation_id
        dismissed = recs.dismiss_recommendation(rec_id)
        self.assertTrue(dismissed)
        self.assertTrue(recs.recommendations[rec_id].dismissed)

    def test_privacy_export_and_reset(self):
        """Test privacy export API and reset data capabilities."""
        engine = AdaptiveIntelligenceEngine()
        engine.preferences.set_preference("preferred_editor", "neovim")

        exported = engine.export_learning_data()
        self.assertIn("preferred_editor", exported["preferences"])

        engine.reset_learning_data()
        reset_pref = engine.preferences.get_preference("preferred_editor")
        self.assertEqual(reset_pref.value, "vscode")


if __name__ == "__main__":
    unittest.main()
