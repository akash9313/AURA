import logging
from computer.models import AutomationResult
from computer.providers.base_provider import BaseComputerProvider

logger = logging.getLogger("AURA.Computer.Mouse")


class MouseController:
    """Mouse automation controller."""

    def __init__(self, provider: BaseComputerProvider):
        self.provider = provider

    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> AutomationResult:
        return self.provider.click_mouse(x, y, button=button, clicks=clicks)

    def drag_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> AutomationResult:
        return self.provider.drag_drop(start_x, start_y, end_x, end_y)
