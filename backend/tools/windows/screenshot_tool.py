import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class ScreenshotTool(Tool):
    """Tool for taking desktop screenshots."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "screenshot"

    @property
    def description(self) -> str:
        return "Captures desktop screen image and saves it to a file path."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        output_path = parameters.get("output_path") or parameters.get("filepath") or "screenshot.png"

        res = self.manager.take_screenshot(output_path)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
