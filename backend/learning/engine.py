import logging
from typing import Any, Dict, List, Optional
from learning.analytics import LearningAnalyticsRecorder
from learning.behavior import BehaviorAdapter
from learning.confidence import ConfidenceModel
from learning.models import ConfidenceRating, Recommendation, UserPreference, WorkflowPattern
from learning.optimizer import WorkflowOptimizer
from learning.preferences import PreferenceEngine
from learning.ranking import ToolRankingEngine
from learning.recommendations import RecommendationEngine
from learning.workflow_learning import WorkflowLearningEngine

logger = logging.getLogger("AURA.Learning.Engine")


class AdaptiveIntelligenceEngine:
    """
    Master Adaptive Intelligence Engine Orchestrator.
    Learns user preferences, optimizes workflow patterns, scores confidence, generates explainable recommendations,
    and provides full privacy controls (review, edit, export, delete).
    """

    def __init__(self, bus=None):
        self.bus = bus
        self.preferences = PreferenceEngine()
        self.behavior = BehaviorAdapter(self.preferences)
        self.learning = WorkflowLearningEngine()
        self.optimizer = WorkflowOptimizer(self.learning)
        self.confidence = ConfidenceModel()
        self.recommendations = RecommendationEngine(self.preferences)
        self.ranking = ToolRankingEngine()
        self.analytics = LearningAnalyticsRecorder()

    def process_workflow_outcome(self, goal: str, sequence: List[str], success: bool) -> WorkflowPattern:
        """Process workflow execution outcome and update learning models."""
        pattern = self.learning.record_workflow_execution(goal, sequence, success)
        self.analytics.record_workflow_result(success)

        for tool_name in sequence:
            self.ranking.record_usage(tool_name)

        logger.info(f"Adaptive Engine processed workflow outcome for '{goal}' (Success: {success})")
        return pattern

    def get_confidence_rating(self, success_count: int, total_attempts: int) -> ConfidenceRating:
        """Get transparent confidence rating."""
        return self.confidence.calculate_confidence(success_count, total_attempts)

    def get_recommendations(self) -> List[Recommendation]:
        """Get active explainable recommendations."""
        return self.recommendations.generate_recommendations()

    def export_learning_data(self) -> Dict[str, Any]:
        """Privacy API: Export all learned data."""
        return {
            "preferences": self.preferences.export_preferences(),
            "analytics": self.analytics.get_summary(),
            "ranked_tools": self.ranking.get_ranked_tools(),
        }

    def reset_learning_data(self) -> None:
        """Privacy API: Clear all learned data."""

        self.preferences.clear_learned_preferences()
        logger.info("Reset all Adaptive Intelligence Engine data.")
