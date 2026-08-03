import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class SwitchTabTool(Tool):
    """Tool for switching active browser tabs."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "switch_tab"

    @property
    def description(self) -> str:
        return "Switches active browser tab by tab index."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        index = int(parameters.get("index", 0))

        res = self.manager.switch_tab(index)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Switched to browser tab {index}",
            data=res.to_dict(),
            execution_time=elapsed
        )
