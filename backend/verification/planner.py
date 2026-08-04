"""
Verification Recovery Planner.
Determines recovery strategy when verification fails (Retry Action, Alternative Strategy, User Confirmation, Abort).
"""

import logging
from typing import Optional

from verification.configuration import GoalVerificationConfig
from verification.models import FailureType

logger = logging.getLogger("AURA.Verification.Planner")


class VerificationRecoveryPlanner:
    """
    Decides recovery action path upon verification failure.
    """

    def __init__(self, config: Optional[GoalVerificationConfig] = None):
        self.config = config or GoalVerificationConfig()

    def determine_recovery_action(
        self,
        failure_type: FailureType,
        attempt_count: int = 1,
    ) -> str:
        """
        Determine recommended recovery path.

        Returns:
            String recovery action directive.
        """
        if not self.config.auto_recovery_enabled:
            return "abort_workflow"

        if attempt_count <= self.config.max_retry_attempts:
            if failure_type == FailureType.ELEMENT_NOT_FOUND:
                return "use_alternative_strategy"
            elif failure_type in (FailureType.STATE_MISMATCH, FailureType.TIMEOUT):
                return "retry_current_action"
            elif failure_type == FailureType.LOW_CONFIDENCE:
                return "use_alternative_strategy"

        return "request_user_confirmation"
