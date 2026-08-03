import logging
import time
from typing import Any, Dict, List, Optional
from browser.cookies import BrowserCookieManager
from browser.downloads import BrowserDownloadHandler
from browser.extractor import BrowserExtractor
from browser.forms import BrowserFormHandler
from browser.history import BrowserHistoryTracker
from browser.models import BrowserActionType, BrowserPermissionLevel, BrowserResult
from browser.navigator import BrowserNavigator
from browser.permissions import BrowserPermissionManager
from browser.sessions import BrowserSessionManager
from browser.tabs import BrowserTabManager

logger = logging.getLogger("AURA.Browser.Controller")


class BrowserController:
    """
    Master Controller tying permissions, logging, sub-managers, and providers together.
    """

    def __init__(self):
        self.permissions = BrowserPermissionManager()
        self.navigator = BrowserNavigator()
        self.extractor = BrowserExtractor()
        self.forms = BrowserFormHandler()
        self.downloads = BrowserDownloadHandler()
        self.tabs = BrowserTabManager()
        self.history = BrowserHistoryTracker()
        self.cookies = BrowserCookieManager()
        self.sessions = BrowserSessionManager()

    def execute_action(self, action_type: BrowserActionType, parameters: Dict[str, Any], action_fn) -> BrowserResult:
        """
        Execute a browser operation with safety permission verification and history logging.

        Args:
            action_type (BrowserActionType): Operation category.
            parameters (Dict[str, Any]): Operation inputs.
            action_fn (Callable): Sub-manager execution lambda.

        Returns:
            BrowserResult: Execution result.
        """
        start_time = time.time()
        is_allowed, level, reason = self.permissions.check_permission(action_type, parameters)

        if not is_allowed:
            elapsed = time.time() - start_time
            return BrowserResult(success=False, metadata={"error": reason}, execution_time=elapsed)

        try:
            result: BrowserResult = action_fn()
            elapsed = time.time() - start_time
            if result.execution_time == 0.0:
                result.execution_time = elapsed

            if result.success and result.url:
                self.history.record(result.url, result.title)

            return result
        except Exception as e:
            elapsed = time.time() - start_time
            err_msg = f"Browser action '{action_type.value}' error: {e}"
            logger.error(err_msg)
            return BrowserResult(success=False, metadata={"error": err_msg}, execution_time=elapsed)
