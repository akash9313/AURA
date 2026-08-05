"""
Desktop Capability Validation Events.
Published to EventBus during desktop validation lifecycle.
"""

from enum import Enum


class DesktopValidationEvent(Enum):
    """Event definitions for Desktop Capability Validation."""
    MISSION_STARTED = "mission_started"
    APPLICATION_LAUNCHED = "application_launched"
    WINDOW_FOCUSED = "window_focused"
    TASK_COMPLETED = "task_completed"
    VERIFICATION_COMPLETED = "verification_completed"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"
