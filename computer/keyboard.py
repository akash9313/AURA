import logging
from typing import List
from computer.models import AutomationResult
from computer.providers.base_provider import BaseComputerProvider

logger = logging.getLogger("AURA.Computer.Keyboard")


class KeyboardController:
    """Keyboard input automation controller."""

    def __init__(self, provider: BaseComputerProvider):
        self.provider = provider

    def type_text(self, text: str) -> AutomationResult:
        return self.provider.type_text(text)

    def press_shortcut(self, keys: List[str]) -> AutomationResult:
        return self.provider.press_shortcut(keys)
