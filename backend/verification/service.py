"""
Goal Verification Service.
Top-level AURA service integrating the Goal Verification Engine into the kernel framework.
Validates whether workflow actions achieved the user's intended objective based on observable empirical evidence.
"""

import logging
from typing import Any, Dict, List, Optional

from core.service import Service
from verification.configuration import GoalVerificationConfig
from verification.models import (
    EvidenceType,
    GoalVerificationRequest,
    GoalVerificationResult,
)
from verification.verifier import GoalVerifier

logger = logging.getLogger("AURA.Verification.Service")


class GoalVerificationService(Service):
    """
    Service wrapper exposing Goal Verification capabilities to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[GoalVerificationConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or GoalVerificationConfig()
        self.verifier = GoalVerifier(bus=bus, config=self.config)
        logger.info("GoalVerificationService initialized")

    async def verify_goal(
        self,
        goal_id: str,
        goal_description: str,
        expected_outcome: Dict[str, Any],
        strategies: Optional[List[EvidenceType]] = None,
        min_confidence_threshold: Optional[float] = None,
    ) -> GoalVerificationResult:
        """
        Verify workflow action goal against empirical observable evidence.

        Returns:
            GoalVerificationResult object.
        """
        req = GoalVerificationRequest(
            goal_id=goal_id,
            goal_description=goal_description,
            expected_outcome=expected_outcome,
            strategies=strategies or [],
            min_confidence_threshold=min_confidence_threshold or self.config.default_confidence_threshold,
        )
        return await self.verifier.verify_goal(req)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting GoalVerificationService...")

    def stop(self) -> None:
        logger.info("Stopping GoalVerificationService...")

    def is_healthy(self) -> bool:
        return True
