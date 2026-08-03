import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class ClickElementTool(Tool):
    """Tool for clicking web page elements."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "click_element"

    @property
    def description(self) -> str:
        return "Clicks a web page button, link, or input element by CSS/XPath selector."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        selector = parameters.get("selector") or parameters.get("element") or ""

        if not selector:
            return ToolResult(
                success=False,
                message="No element selector specified to click.",
                execution_time=time.time() - start_time
            )

        res = self.manager.click_element(selector)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Clicked web element '{selector}'",
            data=res.to_dict(),
            execution_time=elapsed
        )
