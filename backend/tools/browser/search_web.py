import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class SearchWebTool(Tool):
    """Tool for searching the web."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "search_web"

    @property
    def description(self) -> str:
        return "Performs a web search engine query."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        query = parameters.get("query") or parameters.get("search") or ""
        if not query:
            return ToolResult(
                success=False,
                message="No search query provided.",
                execution_time=time.time() - start_time
            )

        res = self.manager.search_web(query)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Searched web for '{query}'",
            data=res.to_dict(),
            execution_time=elapsed
        )
