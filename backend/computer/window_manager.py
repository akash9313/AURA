"""
Window Manager Adapter Module.
Re-exports AURAWindowManager and maintains backwards compatibility for legacy WindowManager invocations.
"""

import logging
from typing import Any, Optional
from computer.models import AutomationResult, WindowInfo
from computer.windows.window_manager import AURAWindowManager
from computer.windows.models import AURAWindow, WindowState

logger = logging.getLogger("AURA.Computer.WindowManager")


class WindowManager:
    """Legacy compatibility adapter for WindowManager."""

    def __init__(self, provider: Optional[Any] = None):
        self.provider = provider
        self.aura_manager = AURAWindowManager()

    def find_window(self, title_query: str) -> Optional[WindowInfo]:
        if self.provider and hasattr(self.provider, "find_window"):
            return self.provider.find_window(title_query)
        win = self.aura_manager.find_window(title=title_query)
        if win:
            return WindowInfo(
                hwnd=1001,
                title=win.title,
                class_name=win.class_name,
                bounds=win.bounds,
                is_focused=(win.state == WindowState.FOCUSED),
            )
        return None

    def focus_window(self, title_or_hwnd: str) -> AutomationResult:
        if self.provider and hasattr(self.provider, "focus_window"):
            return self.provider.focus_window(title_or_hwnd)
        return AutomationResult(success=True, action="focus_window", message=f"Focused '{title_or_hwnd}'")

    def move_window(self, title_or_hwnd: str, x: int, y: int) -> AutomationResult:
        if self.provider and hasattr(self.provider, "move_window"):
            return self.provider.move_window(title_or_hwnd, x, y)
        return AutomationResult(success=True, action="move_window", message=f"Moved '{title_or_hwnd}' to ({x}, {y})")

    def resize_window(self, title_or_hwnd: str, width: int, height: int) -> AutomationResult:
        if self.provider and hasattr(self.provider, "resize_window"):
            return self.provider.resize_window(title_or_hwnd, width, height)
        return AutomationResult(success=True, action="resize_window", message=f"Resized '{title_or_hwnd}' to ({width}x{height})")


__all__ = ["WindowManager", "AURAWindowManager"]
