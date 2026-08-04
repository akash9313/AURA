"""
Navigation Engine Event Definitions.
All navigation lifecycle events published to the AURA EventBus.
"""

from enum import Enum


class NavigationEvent(Enum):
    """Event definitions for Navigation Engine lifecycle and page management."""
    NAVIGATION_STARTED = "navigation_started"
    NAVIGATION_COMPLETED = "navigation_completed"
    NAVIGATION_FAILED = "navigation_failed"
    PAGE_RELOADED = "page_reloaded"
    PAGE_BACK = "page_back"
    PAGE_FORWARD = "page_forward"
    PAGE_STOPPED = "page_stopped"
    REDIRECT_DETECTED = "redirect_detected"
    WAIT_STARTED = "wait_started"
    WAIT_COMPLETED = "wait_completed"
