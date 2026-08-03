import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class MouseClickTool(Tool):
    """Tool for triggering mouse click events."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "mouse_click"

    @property
    def description(self) -> str:
        return "Performs mouse click at current cursor position or specified x, y screen coordinates."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        x = parameters.get("x")
        y = parameters.get("y")
        button = parameters.get("button", "left")
        clicks = int(parameters.get("clicks", 1))

        res = self.manager.mouse_click(x=x, y=y, button=button, clicks=clicks)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
