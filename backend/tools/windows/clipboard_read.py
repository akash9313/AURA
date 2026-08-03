import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class ClipboardReadTool(Tool):
    """Tool for reading system clipboard."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "clipboard_read"

    @property
    def description(self) -> str:
        return "Reads current text contents from Windows system clipboard."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        res = self.manager.clipboard_read()
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
