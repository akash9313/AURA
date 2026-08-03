import logging
import time
import pyperclip
from windows.models import AutomationResult

logger = logging.getLogger("AURA.Windows.Clipboard")


class ClipboardManager:
    """
    Manager responsible for reading, writing, clearing, and inspecting Windows clipboard content.
    """

    def read_text(self) -> AutomationResult:
        """Read text string from system clipboard."""
        start_time = time.time()
        try:
            content = pyperclip.paste()
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message="Clipboard text read successfully.",
                data={"text": content},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Clipboard read error: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to read clipboard: {e}",
                execution_time=elapsed
            )

    def write_text(self, text: str) -> AutomationResult:
        """Copy text string onto system clipboard."""
        start_time = time.time()
        try:
            pyperclip.copy(text)
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message="Text written to clipboard.",
                data={"text": text},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Clipboard write error: {e}")
            return AutomationResult(
                success=False,
                message=f"Failed to write clipboard: {e}",
                execution_time=elapsed
            )

    def clear(self) -> AutomationResult:
        """Clear contents of system clipboard."""
        return self.write_text("")
