import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class ClipboardWriteTool(Tool):
    """Tool for writing text onto system clipboard."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "clipboard_write"

    @property
    def description(self) -> str:
        return "Writes specified text string onto Windows system clipboard."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = parameters.get("text") or parameters.get("content") or ""
        if not text:
            return ToolResult(
                success=False,
                message="No text specified to write to clipboard.",
                execution_time=time.time() - start_time
            )

        res = self.manager.clipboard_write(text)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
