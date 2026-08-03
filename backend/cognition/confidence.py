import logging
from typing import Dict, Any, List
from cognition.models import ConfidenceScore, RiskLevel

logger = logging.getLogger("AURA.Cognition.Confidence")


class ConfidenceEngine:
    """
    Engine evaluating decision confidence ratings, risk assessments, and recommended actions.
    """

    def evaluate_task_risk(self, tool_name: str, parameters: Dict[str, Any]) -> ConfidenceScore:
        """
        Evaluate confidence score and risk level for a proposed tool execution.

        Args:
            tool_name (str): Action tool name.
            parameters (Dict[str, Any]): Input parameters.

        Returns:
            ConfidenceScore: Calculated confidence rating and risk level.
        """
        lower_tool = tool_name.lower()

        # High Risk Operations
        if any(k in lower_tool for k in ["delete", "remove", "format", "shutdown", "payment"]):
            return ConfidenceScore(
                score=0.6,
                reason=f"Operation '{tool_name}' performs destructive/sensitive action.",
                risk_level=RiskLevel.HIGH,
                recommended_action="confirm"
            )

        # Web / Application Launch Operations
        if any(k in lower_tool for k in ["open_application", "open_url", "search_web", "type_text"]):
            return ConfidenceScore(
                score=0.95,
                reason=f"Standard automated action '{tool_name}' is verified.",
                risk_level=RiskLevel.LOW,
                recommended_action="execute"
            )

        # Standard Desktop Queries & Vision
        return ConfidenceScore(
            score=0.9,
            reason=f"Action '{tool_name}' evaluated with high confidence.",
            risk_level=RiskLevel.LOW,
            recommended_action="execute"
        )
