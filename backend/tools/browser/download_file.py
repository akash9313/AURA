import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class DownloadFileTool(Tool):
    """Tool for downloading files from web URLs."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "download_file"

    @property
    def description(self) -> str:
        return "Downloads a file from a web URL to local disk."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        url = parameters.get("url") or parameters.get("file_url") or ""
        output_path = parameters.get("output_path") or "downloaded_file"

        if not url:
            return ToolResult(
                success=False,
                message="No file URL provided for download.",
                execution_time=time.time() - start_time
            )

        res = self.manager.download_file(url, output_path)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Downloaded file from '{url}'",
            data=res.to_dict(),
            execution_time=elapsed
        )
