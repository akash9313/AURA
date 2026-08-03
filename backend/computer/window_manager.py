import logging
from typing import Optional
from computer.models import AutomationResult, WindowInfo
from computer.providers.base_provider import BaseComputerProvider

logger = logging.getLogger("AURA.Computer.WindowManager")


class WindowManager:
    """Window management controller."""

    def __init__(self, provider: BaseComputerProvider):
        self.provider = provider

    def find_window(self, title_query: str) -> Optional[WindowInfo]:
        return self.provider.find_window(title_query)

    def focus_window(self, title_or_hwnd: str) -> AutomationResult:
        return self.provider.focus_window(title_or_hwnd)

    def move_window(self, title_or_hwnd: str, x: int, y: int) -> AutomationResult:
        return self.provider.move_window(title_or_hwnd, x, y)

    def resize_window(self, title_or_hwnd: str, width: int, height: int) -> AutomationResult:
        return self.provider.resize_window(title_or_hwnd, width, height)
