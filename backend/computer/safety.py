import logging
from typing import Callable, Optional, Tuple
from computer.models import ActionType, SafetyLevel

logger = logging.getLogger("AURA.Computer.Safety")


class SafetySystem:
    """
    Action safety policy manager categorizing and enforcing action permission levels.
    """

    ACTION_SAFETY_MAP = {
        ActionType.OPEN_APP: SafetyLevel.NORMAL,
        ActionType.CLOSE_APP: SafetyLevel.SENSITIVE,
        ActionType.FOCUS_WINDOW: SafetyLevel.SAFE,
        ActionType.MOVE_WINDOW: SafetyLevel.SAFE,
        ActionType.RESIZE_WINDOW: SafetyLevel.SAFE,
        ActionType.TYPE_TEXT: SafetyLevel.NORMAL,
        ActionType.KEYBOARD_SHORTCUT: SafetyLevel.NORMAL,
        ActionType.MOUSE_CLICK: SafetyLevel.SAFE,
        ActionType.DRAG_DROP: SafetyLevel.NORMAL,
        ActionType.CLIPBOARD_READ: SafetyLevel.SAFE,
        ActionType.CLIPBOARD_WRITE: SafetyLevel.NORMAL,
        ActionType.EXPLORER_SEARCH: SafetyLevel.SAFE,
        ActionType.SAVE_DIALOG: SafetyLevel.SENSITIVE,
    }

    def __init__(self, confirmation_hook: Optional[Callable[[ActionType, str], bool]] = None):
        self.confirmation_hook = confirmation_hook

    def evaluate_action(self, action: ActionType, details: str = "") -> Tuple[SafetyLevel, bool]:
        safety_level = self.ACTION_SAFETY_MAP.get(action, SafetyLevel.NORMAL)
        logger.info(f"Evaluating SafetyLevel for {action.value}: {safety_level.value}")

        if safety_level in (SafetyLevel.SENSITIVE, SafetyLevel.DANGEROUS):
            if self.confirmation_hook:
                allowed = self.confirmation_hook(action, details)
                return safety_level, allowed
            logger.warning(f"Executing {safety_level.value} action without confirmation hook.")
            return safety_level, True

        return safety_level, True
