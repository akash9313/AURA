"""
AURA Navigation Engine.
Provider-independent browser navigation, page lifecycle, wait strategies, and history management.
"""

from browser.navigation.actions import NavigationActions
from browser.navigation.configuration import NavigationConfig
from browser.navigation.events import NavigationEvent
from browser.navigation.history import NavigationHistory
from browser.navigation.models import (
    NavigationActionType,
    NavigationEntry,
    NavigationErrorType,
    NavigationHealthStatus,
    NavigationHistoryInfo,
    NavigationResult,
    NavigationState,
    RedirectInfo,
    WaitStrategy,
)
from browser.navigation.navigator import Navigator
from browser.navigation.service import NavigationService, PageHandleResolver
from browser.navigation.validator import NavigationValidator
from browser.navigation.waits import WaitStrategyExecutor

__all__ = [
    "NavigationService",
    "Navigator",
    "NavigationActions",
    "WaitStrategyExecutor",
    "NavigationHistory",
    "NavigationValidator",
    "PageHandleResolver",
    "NavigationConfig",
    "NavigationEvent",
    "NavigationState",
    "NavigationActionType",
    "NavigationErrorType",
    "NavigationResult",
    "NavigationEntry",
    "NavigationHistoryInfo",
    "NavigationHealthStatus",
    "RedirectInfo",
    "WaitStrategy",
]
