import logging
from typing import List
from windows.models import AutomationResult
from windows.providers.pyautogui_provider import PyAutoGUIProvider

logger = logging.getLogger("AURA.Windows.Keyboard")


class KeyboardManager:
    """
    Manager responsible for typing text, hotkeys, shortcuts, and key manipulation.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PyAutoGUIProvider()

    def type_text(self, text: str, interval: float = 0.01) -> AutomationResult:
        """Type arbitrary string text."""
        logger.info(f"KeyboardManager typing text of length {len(text)}")
        return self.provider.type_text(text, interval=interval)

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        """Execute hotkey combination (e.g. ['ctrl', 'c'])."""
        logger.info(f"KeyboardManager executing shortcut: {keys}")
        return self.provider.press_shortcut(keys)

    def copy(self) -> AutomationResult:
        """Execute Ctrl+C shortcut."""
        return self.press_shortcut(["ctrl", "c"])

    def paste(self) -> AutomationResult:
        """Execute Ctrl+V shortcut."""
        return self.press_shortcut(["ctrl", "v"])

    def undo(self) -> AutomationResult:
        """Execute Ctrl+Z shortcut."""
        return self.press_shortcut(["ctrl", "z"])

    def redo(self) -> AutomationResult:
        """Execute Ctrl+Y shortcut."""
        return self.press_shortcut(["ctrl", "y"])
