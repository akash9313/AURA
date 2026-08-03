import logging
from typing import Optional
from windows.models import AutomationResult
from windows.providers.pyautogui_provider import PyAutoGUIProvider

logger = logging.getLogger("AURA.Windows.Mouse")


class MouseManager:
    """
    Manager responsible for mouse cursor movements, clicks, scrolling, and dragging.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PyAutoGUIProvider()

    def move(self, x: int, y: int) -> AutomationResult:
        """Move mouse cursor to absolute screen coordinates."""
        return self.provider.click(x=x, y=y, clicks=0)

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> AutomationResult:
        """Perform a single click."""
        return self.provider.click(x=x, y=y, button=button, clicks=1)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> AutomationResult:
        """Perform a double click."""
        return self.provider.click(x=x, y=y, button="left", clicks=2)

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> AutomationResult:
        """Perform a right click."""
        return self.provider.click(x=x, y=y, button="right", clicks=1)
