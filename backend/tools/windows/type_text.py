import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class TypeTextTool(Tool):
    """Tool for typing text into focused element."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "type_text"

    @property
    def description(self) -> str:
        return "Types a text string into the currently focused window or element."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        text = parameters.get("text") or parameters.get("content") or ""
        interval = float(parameters.get("interval", 0.01))

        if not text:
            return ToolResult(
                success=False,
                message="No text string provided to type.",
                execution_time=time.time() - start_time
            )

        res = self.manager.type_text(text, interval=interval)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
