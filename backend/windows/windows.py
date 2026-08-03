import logging
from typing import List, Optional
from windows.models import AutomationResult, WindowInfo
from windows.providers.pyautogui_provider import PyAutoGUIProvider

logger = logging.getLogger("AURA.Windows.WindowManager")


class WindowManager:
    """
    Manager responsible for enumerating, focusing, minimizing, maximizing, and manipulating Windows.
    """

    def __init__(self, provider=None):
        self.provider = provider if provider is not None else PyAutoGUIProvider()

    def focus_window(self, title: str) -> AutomationResult:
        """Bring target window to foreground."""
        logger.info(f"Focusing window matching title: '{title}'")
        return self.provider.focus_window(title)

    def enumerate_windows(self) -> List[WindowInfo]:
        """Get all visible desktop windows."""
        return self.provider.list_windows()

    def get_active_window(self) -> Optional[WindowInfo]:
        """Retrieve currently focused active window."""
        windows = self.enumerate_windows()
        for w in windows:
            if w.is_active:
                return w
        return windows[0] if windows else None
