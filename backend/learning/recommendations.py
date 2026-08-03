import logging
import uuid
from typing import Dict, List, Optional
from learning.models import Recommendation, RiskLevel
from learning.preferences import PreferenceEngine

logger = logging.getLogger("AURA.Learning.Recommendations")


class RecommendationEngine:
    """
    Generates explainable, dismissible suggestions based on learned user preferences and workflow patterns.
    """

    def __init__(self, preference_engine: PreferenceEngine):
        self.preference_engine = preference_engine
        self.recommendations: Dict[str, Recommendation] = {}

    def generate_recommendations(self) -> List[Recommendation]:
        """Generate explainable recommendations for the user."""

        recs = []

        browser_pref = self.preference_engine.get_preference("preferred_browser")
        if browser_pref and browser_pref.source == "inferred":
            rec_id = f"rec_{uuid.uuid4().hex[:8]}"
            r = Recommendation(
                recommendation_id=rec_id,
                title=f"Set Default Browser to {browser_pref.value.capitalize()}",
                reason=f"You typically use {browser_pref.value.capitalize()} instead of system default.",
                supporting_evidence=[f"Observed repeated launch of {browser_pref.value}"],
                confidence_score=browser_pref.confidence_score,
                risk_level=RiskLevel.LOW
            )
            self.recommendations[rec_id] = r
            recs.append(r)

        return recs

    def dismiss_recommendation(self, recommendation_id: str) -> bool:
        """Dismiss a recommendation."""
        r = self.recommendations.get(recommendation_id)
        if r:
            r.dismissed = True
            logger.info(f"Dismissed recommendation '{recommendation_id}'")
            return True
        return False
