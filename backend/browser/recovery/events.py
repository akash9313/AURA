"""
Browser Recovery Engine Event Definitions.
Published to AURA EventBus during recovery initiation, retry backoffs, state restorations, and browser restarts.
"""

from enum import Enum


class RecoveryEvent(Enum):
    """Event definitions for Browser Recovery Subsystem."""
    RECOVERY_STARTED = "recovery_started"
    RECOVERY_COMPLETED = "recovery_completed"
    RECOVERY_FAILED = "recovery_failed"
    RETRY_STARTED = "retry_started"
    RETRY_COMPLETED = "retry_completed"
    STATE_RESTORED = "state_restored"
    BROWSER_RESTARTED = "browser_restarted"
