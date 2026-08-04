"""
Recovery Engine Configuration Management.
Provides configurable backoff policies, threshold limits, strategy mappings, and feature toggles.
"""

from dataclasses import dataclass, field
from typing import Dict

from browser.recovery.models import BackoffStrategy, FailureType, RecoveryStrategy


@dataclass
class RecoveryConfig:
    """Configurable parameters for Recovery Engine."""
    max_retries: int = 3
    default_backoff: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_backoff_ms: float = 500.0
    max_backoff_ms: float = 10000.0
    backoff_multiplier: float = 2.0
    enable_snapshots: bool = True
    enable_self_healing: bool = True
    enable_health_monitoring: bool = True
    health_check_interval_ms: float = 5000.0
    max_memory_mb: float = 2048.0
    max_crash_threshold: int = 5

    # Configurable mapping from FailureType to RecoveryStrategy
    strategy_mapping: Dict[FailureType, RecoveryStrategy] = field(
        default_factory=lambda: {
            FailureType.NAVIGATION_TIMEOUT: RecoveryStrategy.REFRESH_PAGE,
            FailureType.DNS_FAILURE: RecoveryStrategy.RETRY,
            FailureType.SSL_FAILURE: RecoveryStrategy.ABORT_WORKFLOW,
            FailureType.BROWSER_CRASH: RecoveryStrategy.RESTART_BROWSER,
            FailureType.PAGE_CRASH: RecoveryStrategy.RECREATE_PAGE,
            FailureType.ELEMENT_MISSING: RecoveryStrategy.FALLBACK_LOCATOR,
            FailureType.ELEMENT_DETACHED: RecoveryStrategy.RETRY,
            FailureType.DOM_CHANGED: RecoveryStrategy.FALLBACK_LOCATOR,
            FailureType.POPUP_BLOCKED: RecoveryStrategy.RETRY,
            FailureType.UNEXPECTED_REDIRECT: RecoveryStrategy.ALTERNATIVE_NAVIGATION,
            FailureType.DOWNLOAD_FAILURE: RecoveryStrategy.RETRY,
            FailureType.UPLOAD_FAILURE: RecoveryStrategy.RETRY,
            FailureType.AUTHENTICATION_EXPIRED: RecoveryStrategy.RESTORE_SESSION,
            FailureType.SESSION_LOST: RecoveryStrategy.RESTORE_SESSION,
            FailureType.NETWORK_OFFLINE: RecoveryStrategy.RETRY,
            FailureType.UNKNOWN: RecoveryStrategy.REFRESH_PAGE,
        }
    )
