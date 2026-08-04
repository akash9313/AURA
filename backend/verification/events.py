"""
Goal Verification Event Definitions.
Published to AURA EventBus during verification lifecycle, confidence scoring, and recovery requests.
"""

from enum import Enum


class VerificationEvent(Enum):
    """Event definitions for Goal Verification Engine."""
    GOAL_VERIFICATION_STARTED = "goal_verification_started"
    GOAL_VERIFIED = "goal_verified"
    GOAL_FAILED = "goal_failed"
    CONFIDENCE_UPDATED = "confidence_updated"
    RECOVERY_REQUESTED = "recovery_requested"
