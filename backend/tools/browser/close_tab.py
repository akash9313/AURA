import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class CloseTabTool(Tool):
    """Tool for closing browser tabs."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "close_tab"

    @property
    def description(self) -> str:
        return "Closes open browser tab by tab index."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        index = int(parameters.get("index", -1))

        res = self.manager.close_tab(index)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message="Closed browser tab.",
            data=res.to_dict(),
            execution_time=elapsed
        )
