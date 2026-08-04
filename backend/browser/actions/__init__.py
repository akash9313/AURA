"""
AURA Browser Action Engine.
High-level, human-like, reliable browser action execution and interaction subsystem.
"""

from browser.actions.action_engine import ActionEngine
from browser.actions.click import ClickActionExecutor
from browser.actions.download import DownloadActionExecutor
from browser.actions.events import ActionEvent
from browser.actions.forms import FormActionExecutor
from browser.actions.locator import SmartElementLocator
from browser.actions.models import (
    ActionEngineConfig,
    ActionHealthStatus,
    ActionOptions,
    ActionResult,
    ActionState,
    ActionType,
    DownloadResult,
    LocatorStrategy,
    ScrollDirection,
    TargetElement,
)
from browser.actions.scrolling import ScrollActionExecutor
from browser.actions.service import BrowserActionService
from browser.actions.typing import TypingActionExecutor
from browser.actions.upload import UploadActionExecutor
from browser.actions.verification import ActionVerifier
from browser.actions.waits import ActionWaitExecutor

__all__ = [
    "BrowserActionService",
    "ActionEngine",
    "SmartElementLocator",
    "ActionWaitExecutor",
    "ActionVerifier",
    "ClickActionExecutor",
    "TypingActionExecutor",
    "ScrollActionExecutor",
    "FormActionExecutor",
    "UploadActionExecutor",
    "DownloadActionExecutor",
    "ActionEngineConfig",
    "ActionHealthStatus",
    "ActionOptions",
    "ActionResult",
    "DownloadResult",
    "TargetElement",
    "ActionType",
    "LocatorStrategy",
    "ActionState",
    "ScrollDirection",
    "ActionEvent",
]
