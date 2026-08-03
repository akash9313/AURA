import logging
from typing import Any, Dict, Tuple
from windows.models import ActionType, PermissionLevel

logger = logging.getLogger("AURA.Windows.Permissions")


class PermissionManager:
    """
    Manages safety permissions, policy enforcement, and confirmation requirements for OS actions.
    """

    def __init__(self):
        self._policy: Dict[ActionType, PermissionLevel] = {
            ActionType.LAUNCH_APP: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.CLOSE_APP: PermissionLevel.REQUIRES_CONFIRMATION,
            ActionType.FOCUS_WINDOW: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.TYPE_TEXT: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.HOTKEY: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.CLICK: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.DRAG: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.CLIPBOARD_READ: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.CLIPBOARD_WRITE: PermissionLevel.ALWAYS_ALLOWED,
            ActionType.SCREENSHOT: PermissionLevel.ALWAYS_ALLOWED,
        }

    def check_permission(self, action_type: ActionType, parameters: Dict[str, Any] = None) -> Tuple[bool, PermissionLevel, str]:
        """
        Evaluate if an action is permitted under current safety policy.

        Returns:
            Tuple[bool, PermissionLevel, str]: (is_allowed, permission_level, reason_message)
        """
        level = self._policy.get(action_type, PermissionLevel.ALWAYS_ALLOWED)

        if level == PermissionLevel.BLOCKED:
            msg = f"Action '{action_type.value}' is blocked by system policy."
            logger.warning(msg)
            return False, level, msg

        if level == PermissionLevel.REQUIRES_CONFIRMATION:
            msg = f"Action '{action_type.value}' requires user confirmation."
            logger.info(msg)
            # Default auto-approval for non-destructive standard desktop tasks
            return True, level, msg

        return True, level, f"Action '{action_type.value}' is allowed."

    def set_permission_level(self, action_type: ActionType, level: PermissionLevel) -> None:
        """Update permission level for a given action type."""
        self._policy[action_type] = level
        logger.info(f"Updated permission for '{action_type.value}' to '{level.value}'")
