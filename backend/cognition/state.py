import logging
from typing import Any, Dict, Optional
from cognition.models import CognitiveStateSnapshot, ConfidenceScore, RiskLevel

logger = logging.getLogger("AURA.Cognition.State")


class CognitiveStateManager:
    """
    Manager maintaining active user, current goal, workflow state, active tool, and context memory snapshots.
    """

    def __init__(self):
        self.user_id: str = "default_user"
        self.current_goal_id: str = ""
        self.current_workflow_id: str = ""
        self.active_tool: str = ""
        self.current_context: Dict[str, Any] = {}
        self.memory_snapshot: Dict[str, Any] = {}
        self.confidence: ConfidenceScore = ConfidenceScore(score=1.0, reason="Initial state", risk_level=RiskLevel.LOW)

    def set_goal(self, goal_id: str) -> None:
        self.current_goal_id = goal_id
        logger.info(f"CognitiveState set active goal_id: '{goal_id}'")

    def set_workflow(self, workflow_id: str) -> None:
        self.current_workflow_id = workflow_id
        logger.info(f"CognitiveState set active workflow_id: '{workflow_id}'")

    def set_active_tool(self, tool_name: str) -> None:
        self.active_tool = tool_name

    def update_confidence(self, score: float, reason: str, risk_level: RiskLevel = RiskLevel.LOW) -> None:
        self.confidence = ConfidenceScore(score=score, reason=reason, risk_level=risk_level)
        logger.info(f"CognitiveState confidence updated: {score:.2f} ({risk_level.value}) - {reason}")

    def capture_snapshot(self) -> CognitiveStateSnapshot:
        """Capture immutable state snapshot for timeline logging."""
        return CognitiveStateSnapshot(
            user_id=self.user_id,
            goal_id=self.current_goal_id,
            workflow_id=self.current_workflow_id,
            active_tool=self.active_tool,
            confidence=self.confidence.score
        )
