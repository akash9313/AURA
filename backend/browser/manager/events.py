from enum import Enum


class BrowserManagerEvent(Enum):
    """Event definitions for Playwright Browser Manager Lifecycle & Context Management."""
    BROWSER_STARTED = "browser_started"
    BROWSER_STOPPED = "browser_stopped"
    BROWSER_CRASHED = "browser_crashed"
    CONTEXT_CREATED = "context_created"
    CONTEXT_DESTROYED = "context_destroyed"
    PAGE_CREATED = "page_created"
    PAGE_CLOSED = "page_closed"
    PAGE_SWITCHED = "page_switched"
