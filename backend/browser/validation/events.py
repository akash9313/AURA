"""
Browser Capability Validation Events.
Published to EventBus during validation lifecycle.
"""

from enum import Enum


class BrowserValidationEvent(Enum):
    """Event definitions for Browser Capability Validation."""
    MISSION_STARTED = "mission_started"
    CAPABILITY_STARTED = "capability_started"
    VERIFICATION_COMPLETED = "verification_completed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"
