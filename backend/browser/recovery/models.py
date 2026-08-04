"""
Browser Recovery & Self-Healing Domain Models.
Defines failure classifications, recovery strategies, backoff types, state snapshots, diagnostics, and health telemetry.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FailureType(Enum):
    """Classified browser and interaction failure types."""
    NAVIGATION_TIMEOUT = "navigation_timeout"
    DNS_FAILURE = "dns_failure"
    SSL_FAILURE = "ssl_failure"
    BROWSER_CRASH = "browser_crash"
    PAGE_CRASH = "page_crash"
    ELEMENT_MISSING = "element_missing"
    ELEMENT_DETACHED = "element_detached"
    DOM_CHANGED = "dom_changed"
    POPUP_BLOCKED = "popup_blocked"
    UNEXPECTED_REDIRECT = "unexpected_redirect"
    DOWNLOAD_FAILURE = "download_failure"
    UPLOAD_FAILURE = "upload_failure"
    AUTHENTICATION_EXPIRED = "authentication_expired"
    SESSION_LOST = "session_lost"
    NETWORK_OFFLINE = "network_offline"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Available recovery and self-healing strategies."""
    RETRY = "retry"
    REFRESH_PAGE = "refresh_page"
    RECREATE_PAGE = "recreate_page"
    RECREATE_CONTEXT = "recreate_context"
    RESTART_BROWSER = "restart_browser"
    RESTORE_SESSION = "restore_session"
    FALLBACK_LOCATOR = "fallback_locator"
    ALTERNATIVE_NAVIGATION = "alternative_navigation"
    ABORT_WORKFLOW = "abort_workflow"


class BackoffStrategy(Enum):
    """Backoff delay calculation policies."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"


class RecoveryState(Enum):
    """Lifecycle state of the Recovery Engine."""
    IDLE = "idle"
    MONITORING = "monitoring"
    RECOVERING = "recovering"
    RESTORING = "restoring"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StateSnapshot:
    """Captured browser and page state snapshot for post-crash recovery."""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    current_url: str = ""
    navigation_history: List[str] = field(default_factory=list)
    session_id: Optional[str] = None
    page_id: Optional[str] = None
    workflow_id: Optional[str] = None
    page_state: Dict[str, Any] = field(default_factory=dict)
    form_values: Dict[str, str] = field(default_factory=dict)
    cookie_metadata: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "current_url": self.current_url,
            "navigation_history": self.navigation_history,
            "session_id": self.session_id,
            "page_id": self.page_id,
            "workflow_id": self.workflow_id,
            "page_state": self.page_state,
            "form_values": self.form_values,
            "cookie_metadata": self.cookie_metadata,
        }


@dataclass
class DiagnosticReport:
    """Structured failure diagnostic report."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    failure_type: FailureType = FailureType.UNKNOWN
    root_cause: str = ""
    recovery_attempted: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None
    success: bool = False
    duration_ms: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "failure_type": self.failure_type.value,
            "root_cause": self.root_cause,
            "recovery_attempted": self.recovery_attempted,
            "recovery_strategy": self.recovery_strategy.value if self.recovery_strategy else None,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "recommendations": self.recommendations,
        }


@dataclass
class HealthMetrics:
    """Browser infrastructure health telemetry metrics."""
    process_alive: bool = True
    page_responsive: bool = True
    memory_mb: float = 0.0
    navigation_latency_ms: float = 0.0
    crash_count: int = 0
    healthy: bool = True
    last_check_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "process_alive": self.process_alive,
            "page_responsive": self.page_responsive,
            "memory_mb": self.memory_mb,
            "navigation_latency_ms": self.navigation_latency_ms,
            "crash_count": self.crash_count,
            "healthy": self.healthy,
            "last_check_timestamp": self.last_check_timestamp,
        }
