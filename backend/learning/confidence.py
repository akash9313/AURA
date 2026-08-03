import logging
from typing import List
from learning.models import ConfidenceRating, RiskLevel

logger = logging.getLogger("AURA.Learning.Confidence")


class ConfidenceModel:
    """
    Computes transparent numeric confidence ratings (0.0 to 1.0) and risk levels based on empirical evidence.
    """

    def calculate_confidence(self, success_count: int, total_attempts: int, action_type: str = "normal") -> ConfidenceRating:
        """
        Calculate transparent confidence rating and risk level.

        Args:
            success_count (int): Total successful runs.
            total_attempts (int): Total run attempts.
            action_type (str): Domain action type.

        Returns:
            ConfidenceRating: Rating payload with evidence.
        """
        if total_attempts == 0:
            return ConfidenceRating(
                score=0.5,
                evidence=["No prior execution history available"],
                risk_level=RiskLevel.MEDIUM,
                reasoning="Default baseline score assigned to unverified action."
            )

        score = round(success_count / float(total_attempts), 2)
        evidence = [f"{success_count} of {total_attempts} prior runs succeeded."]

        if score >= 0.85:
            risk = RiskLevel.LOW
            reasoning = "High empirical success rate observed over prior runs."
        elif score >= 0.5:
            risk = RiskLevel.MEDIUM
            reasoning = "Moderate success rate observed; proceed with caution."
        else:
            risk = RiskLevel.HIGH
            reasoning = "Low empirical success rate observed over prior runs."

        return ConfidenceRating(score=score, evidence=evidence, risk_level=risk, reasoning=reasoning)
