"""
Browser Event Type Enum Definitions.
Categorized into Browser Lifecycle, Session, Navigation, DOM Intelligence, Actions, Verification, Retry, and Vision.
"""

from enum import Enum


class BrowserEventType(Enum):
    """Categorized Browser Subsystem Event Types."""

    # Browser Lifecycle
    BROWSER_STARTED = "browser_started"
    BROWSER_STOPPED = "browser_stopped"
    BROWSER_RESTARTED = "browser_restarted"
    BROWSER_ERROR = "browser_error"

    # Session
    SESSION_CREATED = "session_created"
    SESSION_RESTORED = "session_restored"
    SESSION_DESTROYED = "session_destroyed"

    # Navigation
    NAVIGATION_STARTED = "navigation_started"
    NAVIGATION_COMPLETED = "navigation_completed"
    NAVIGATION_FAILED = "navigation_failed"
    PAGE_LOADED = "page_loaded"
    PAGE_RELOADED = "page_reloaded"
    PAGE_NAVIGATED = "page_navigated"

    # DOM Intelligence
    DOM_PARSED = "dom_parsed"
    ARTICLE_EXTRACTED = "article_extracted"
    TABLE_EXTRACTED = "table_extracted"
    FORM_DETECTED = "form_detected"
    LINKS_EXTRACTED = "links_extracted"
    MEDIA_EXTRACTED = "media_extracted"
    SNAPSHOT_TAKEN = "snapshot_taken"

    # Browser Actions
    CLICK_STARTED = "click_started"
    CLICK_COMPLETED = "click_completed"
    TEXT_TYPED = "text_typed"
    FORM_SUBMITTED = "form_submitted"
    FILE_UPLOADED = "file_uploaded"
    FILE_DOWNLOADED = "file_downloaded"

    # Verification & Retry
    ACTION_VERIFIED = "action_verified"
    ACTION_FAILED = "action_failed"
    ACTION_RETRY = "action_retry"

    # Vision Integration
    SCREENSHOT_CREATED = "screenshot_created"
    UI_CHANGED = "ui_changed"


# Backwards compatibility alias
BrowserEvent = BrowserEventType
