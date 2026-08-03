import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class FocusWindowTool(Tool):
    """Tool for focusing active window by title."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "focus_window"

    @property
    def description(self) -> str:
        return "Brings target desktop window to foreground by window title."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        title = parameters.get("title") or parameters.get("window_title") or ""
        if not title:
            return ToolResult(
                success=False,
                message="No window title specified.",
                execution_time=time.time() - start_time
            )

        res = self.manager.focus_window(title)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
