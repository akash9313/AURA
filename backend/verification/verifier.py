"""
Master Goal Verifier Engine.
Orchestrates Verification Strategies, Evidence Collector, Evidence Comparator, Confidence Scorer, and Recovery Planner.
Ensures actions are verified against observable empirical evidence without assuming success.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from verification.comparator import EvidenceComparator
from verification.confidence import ConfidenceScorer
from verification.configuration import GoalVerificationConfig
from verification.events import VerificationEvent
from verification.evidence import EvidenceCollector
from verification.models import (
    EvidenceType,
    FailureType,
    GoalVerificationRequest,
    GoalVerificationResult,
)
from verification.planner import VerificationRecoveryPlanner
from verification.strategies import (
    ApplicationStateStrategy,
    BrowserDOMStrategy,
    FileSystemStrategy,
    OCRStrategy,
    ScreenVisionStrategy,
    UIAutomationStrategy,
    VerificationStrategy,
    WorkflowEventStrategy,
)

logger = logging.getLogger("AURA.Verification.Verifier")


class GoalVerifier:
    """
    Production-grade Goal Verification Engine master controller.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[GoalVerificationConfig] = None,
    ):
        self.bus = bus
        self.config = config or GoalVerificationConfig()

        self.collector = EvidenceCollector()
        self.comparator = EvidenceComparator()
        self.scorer = ConfidenceScorer()
        self.planner = VerificationRecoveryPlanner(config=self.config)

        self._strategy_map: Dict[EvidenceType, VerificationStrategy] = {
            EvidenceType.APPLICATION_STATE: ApplicationStateStrategy(),
            EvidenceType.FILE_SYSTEM: FileSystemStrategy(),
            EvidenceType.BROWSER_DOM: BrowserDOMStrategy(),
            EvidenceType.UI_AUTOMATION: UIAutomationStrategy(),
            EvidenceType.SCREEN_VISION: ScreenVisionStrategy(),
            EvidenceType.OCR: OCRStrategy(),
            EvidenceType.WORKFLOW_EVENT: WorkflowEventStrategy(),
        }

        logger.info("GoalVerifier initialized")

    async def verify_goal(self, request: GoalVerificationRequest) -> GoalVerificationResult:
        """
        Verify workflow action goal against empirical observable evidence.

        Args:
            request: GoalVerificationRequest details.

        Returns:
            GoalVerificationResult object.
        """
        start_time = time.time()
        logger.info(f"Starting verification for goal '{request.goal_id}' ('{request.goal_description}')...")
        self._publish_event(VerificationEvent.GOAL_VERIFICATION_STARTED, {"goal_id": request.goal_id})

        self.collector.clear()

        # Determine strategies to run
        strategies_to_run = request.strategies or list(self._strategy_map.keys())

        # Collect evidence across strategies
        for strat_type in strategies_to_run:
            strategy = self._strategy_map.get(strat_type)
            if strategy:
                try:
                    await strategy.collect_evidence(request.expected_outcome, self.collector)
                except Exception as e:
                    logger.warning(f"Strategy '{strat_type.value}' collection error: {e}")

        evidence_chain = self.collector.get_evidence_chain()

        # Compare expected outcome vs evidence
        matches, reason, failure_type = self.comparator.compare(request.expected_outcome, evidence_chain)

        # Calculate confidence score
        confidence = self.scorer.calculate_confidence(evidence_chain)
        self._publish_event(VerificationEvent.CONFIDENCE_UPDATED, {"goal_id": request.goal_id, "confidence": confidence})

        min_threshold = request.min_confidence_threshold or self.config.default_confidence_threshold
        verified = matches and (confidence >= min_threshold)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        recovery_action = None

        if verified:
            logger.info(f"Goal '{request.goal_id}' VERIFIED successfully (Conf: {confidence}, Time: {duration_ms}ms)")
            result = GoalVerificationResult(
                verified=True,
                confidence_score=confidence,
                evidence_list=evidence_chain,
                reason=reason,
                failure_type=FailureType.NONE,
                recovery_action=None,
                duration_ms=duration_ms,
            )
            self._publish_event(VerificationEvent.GOAL_VERIFIED, result.to_dict())
            return result

        # Goal failed verification -> Determine recovery action
        if confidence < min_threshold and matches:
            failure_type = FailureType.LOW_CONFIDENCE
            reason = f"Confidence score ({confidence}) below minimum threshold ({min_threshold})"

        recovery_action = self.planner.determine_recovery_action(failure_type)
        logger.warning(f"Goal '{request.goal_id}' FAILED verification ({reason}). Recovery directive: {recovery_action}")

        result = GoalVerificationResult(
            verified=False,
            confidence_score=confidence,
            evidence_list=evidence_chain,
            reason=reason,
            failure_type=failure_type,
            recovery_action=recovery_action,
            duration_ms=duration_ms,
        )

        self._publish_event(VerificationEvent.GOAL_FAILED, result.to_dict())
        self._publish_event(VerificationEvent.RECOVERY_REQUESTED, {"goal_id": request.goal_id, "recovery_action": recovery_action})

        return result

    def _publish_event(self, event: VerificationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish verification event '{event.value}': {e}")
