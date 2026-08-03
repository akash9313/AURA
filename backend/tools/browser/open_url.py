import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class OpenURLTool(Tool):
    """Tool for navigating to a web URL."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "open_url"

    @property
    def description(self) -> str:
        return "Opens a target website URL in the web browser."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        url = parameters.get("url") or parameters.get("link") or ""
        if not url:
            return ToolResult(
                success=False,
                message="No URL provided for browsing.",
                execution_time=time.time() - start_time
            )

        res = self.manager.open_url(url)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Opened '{res.url}' - {res.title}",
            data=res.to_dict(),
            execution_time=elapsed
        )
