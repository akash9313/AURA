"""
AURA Browser Recovery & Self-Healing Engine.
Provides automated recovery from browser crashes, navigation timeouts, session loss, and detached DOM nodes.
"""

from browser.recovery.configuration import RecoveryConfig
from browser.recovery.diagnostics import DiagnosticEngine
from browser.recovery.events import RecoveryEvent
from browser.recovery.fallback import FallbackManager
from browser.recovery.health_monitor import HealthMonitor
from browser.recovery.models import (
    BackoffStrategy,
    DiagnosticReport,
    FailureType,
    HealthMetrics,
    RecoveryState,
    RecoveryStrategy,
    StateSnapshot,
)
from browser.recovery.recovery_engine import BrowserRecoveryEngine
from browser.recovery.retry_engine import RetryEngine
from browser.recovery.service import BrowserRecoveryService
from browser.recovery.state_snapshot import SnapshotManager

__all__ = [
    "BrowserRecoveryService",
    "BrowserRecoveryEngine",
    "RetryEngine",
    "SnapshotManager",
    "DiagnosticEngine",
    "FallbackManager",
    "HealthMonitor",
    "RecoveryConfig",
    "FailureType",
    "RecoveryStrategy",
    "BackoffStrategy",
    "RecoveryState",
    "StateSnapshot",
    "DiagnosticReport",
    "HealthMetrics",
    "RecoveryEvent",
]
