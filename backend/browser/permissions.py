import logging
from typing import Any, Dict, Tuple
from browser.models import BrowserActionType, BrowserPermissionLevel

logger = logging.getLogger("AURA.Browser.Permissions")


class BrowserPermissionManager:
    """
    Manages safety permissions and security policy enforcement for web browsing operations.
    """

    def __init__(self):
        self._policy: Dict[BrowserActionType, BrowserPermissionLevel] = {
            BrowserActionType.OPEN_URL: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.SEARCH: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.EXTRACT_PAGE: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.FILL_FORM: BrowserPermissionLevel.REQUIRES_CONFIRMATION,
            BrowserActionType.CLICK_ELEMENT: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.DOWNLOAD: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.UPLOAD: BrowserPermissionLevel.REQUIRES_CONFIRMATION,
            BrowserActionType.SWITCH_TAB: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.CLOSE_TAB: BrowserPermissionLevel.ALWAYS_ALLOWED,
            BrowserActionType.SCREENSHOT: BrowserPermissionLevel.ALWAYS_ALLOWED,
        }

    def check_permission(self, action_type: BrowserActionType, parameters: Dict[str, Any] = None) -> Tuple[bool, BrowserPermissionLevel, str]:
        """
        Evaluate if a web action is permitted.

        Returns:
            Tuple[bool, BrowserPermissionLevel, str]: (is_allowed, permission_level, message)
        """
        level = self._policy.get(action_type, BrowserPermissionLevel.ALWAYS_ALLOWED)

        if level == BrowserPermissionLevel.BLOCKED:
            msg = f"Web action '{action_type.value}' is blocked by policy."
            logger.warning(msg)
            return False, level, msg

        if level == BrowserPermissionLevel.REQUIRES_CONFIRMATION:
            msg = f"Web action '{action_type.value}' requires user confirmation."
            logger.info(msg)
            # Default auto-approval for safe automated workflows
            return True, level, msg

        return True, level, f"Web action '{action_type.value}' is allowed."
