import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class ScreenshotPageTool(Tool):
    """Tool for taking web browser screenshots."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "screenshot_page"

    @property
    def description(self) -> str:
        return "Captures a screenshot of the currently active browser web page."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        output_path = parameters.get("output_path") or "browser_screenshot.png"

        res = self.manager.screenshot_page(output_path)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message="Browser screenshot captured.",
            data=res.to_dict(),
            execution_time=elapsed
        )
