import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class ExtractPageTool(Tool):
    """Tool for extracting web page structured text and elements."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "extract_page"

    @property
    def description(self) -> str:
        return "Extracts structured text, links, and HTML elements from active or target web page."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        url = parameters.get("url")

        res = self.manager.extract_page(url)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Extracted content from '{res.url}'",
            data=res.to_dict(),
            execution_time=elapsed
        )
