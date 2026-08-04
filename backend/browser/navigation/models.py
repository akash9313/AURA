"""
Navigation Engine Domain Models.
Provider-independent data structures for browser navigation, page lifecycle, and history tracking.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NavigationState(Enum):
    """State of a navigation operation."""
    IDLE = "idle"
    NAVIGATING = "navigating"
    LOADING = "loading"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class WaitStrategy(Enum):
    """Configurable page-load wait strategies."""
    DOM_READY = "dom_ready"
    LOAD_EVENT = "load_event"
    NETWORK_IDLE = "network_idle"
    CUSTOM_SELECTOR = "custom_selector"
    CUSTOM_TIMEOUT = "custom_timeout"
    NONE = "none"


class NavigationActionType(Enum):
    """Types of navigation actions."""
    OPEN_URL = "open_url"
    RELOAD = "reload"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    STOP_LOADING = "stop_loading"


class NavigationErrorType(Enum):
    """Classification of navigation failures."""
    INVALID_URL = "invalid_url"
    UNSUPPORTED_PROTOCOL = "unsupported_protocol"
    DNS_FAILURE = "dns_failure"
    SSL_ERROR = "ssl_error"
    TIMEOUT = "timeout"
    REDIRECT_LOOP = "redirect_loop"
    PAGE_LOAD_FAILURE = "page_load_failure"
    BROWSER_CRASH = "browser_crash"
    NAVIGATION_CANCELLED = "navigation_cancelled"
    UNKNOWN = "unknown"


@dataclass
class RedirectInfo:
    """Single redirect hop metadata."""
    from_url: str
    to_url: str
    status_code: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_url": self.from_url,
            "to_url": self.to_url,
            "status_code": self.status_code,
            "timestamp": self.timestamp,
        }


@dataclass
class NavigationEntry:
    """Single entry in navigation history."""
    url: str
    title: str = ""
    timestamp: float = field(default_factory=time.time)
    load_time_ms: float = 0.0
    action_type: NavigationActionType = NavigationActionType.OPEN_URL
    redirect_chain: List[RedirectInfo] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "load_time_ms": self.load_time_ms,
            "action_type": self.action_type.value,
            "redirect_count": len(self.redirect_chain),
            "success": self.success,
            "error": self.error,
        }


@dataclass
class NavigationResult:
    """Result of a navigation operation returned to callers."""
    success: bool
    url: str = ""
    title: str = ""
    load_time_ms: float = 0.0
    redirect_count: int = 0
    redirect_chain: List[RedirectInfo] = field(default_factory=list)
    error_type: Optional[NavigationErrorType] = None
    error_message: Optional[str] = None
    state: NavigationState = NavigationState.COMPLETED
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "url": self.url,
            "title": self.title,
            "load_time_ms": self.load_time_ms,
            "redirect_count": self.redirect_count,
            "error_type": self.error_type.value if self.error_type else None,
            "error_message": self.error_message,
            "state": self.state.value,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp,
        }


@dataclass
class NavigationHistoryInfo:
    """Summary of navigation history for a page."""
    page_id: str
    current_url: str
    current_title: str
    entries_count: int
    can_go_back: bool
    can_go_forward: bool
    total_redirects: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "current_url": self.current_url,
            "current_title": self.current_title,
            "entries_count": self.entries_count,
            "can_go_back": self.can_go_back,
            "can_go_forward": self.can_go_forward,
            "total_redirects": self.total_redirects,
        }


@dataclass
class NavigationHealthStatus:
    """Health telemetry for the Navigation Engine."""
    state: NavigationState
    total_navigations: int
    successful_navigations: int
    failed_navigations: int
    average_load_time_ms: float
    active_page_id: Optional[str] = None
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "total_navigations": self.total_navigations,
            "successful_navigations": self.successful_navigations,
            "failed_navigations": self.failed_navigations,
            "average_load_time_ms": self.average_load_time_ms,
            "active_page_id": self.active_page_id,
            "last_error": self.last_error,
        }
