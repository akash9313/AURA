import logging
from computer.models import AutomationResult
from computer.providers.base_provider import BaseComputerProvider

logger = logging.getLogger("AURA.Computer.Clipboard")


class ClipboardController:
    """Clipboard controller."""

    def __init__(self, provider: BaseComputerProvider):
        self.provider = provider

    def read_text(self) -> str:
        return self.provider.get_clipboard_text()


    def write_text(self, text: str) -> AutomationResult:
        success = self.provider.set_clipboard_text(text)
        return AutomationResult(
            success=success,
            action="clipboard_write",
            message=f"Copied '{text[:20]}...' to clipboard" if success else "Failed to write to clipboard"
        )
