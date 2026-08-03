import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class UploadFileTool(Tool):
    """Tool for uploading local files to web forms."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "upload_file"

    @property
    def description(self) -> str:
        return "Uploads a local file to a web input file element."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        selector = parameters.get("selector") or "input[type='file']"
        filepath = parameters.get("filepath") or parameters.get("path") or ""

        if not filepath:
            return ToolResult(
                success=False,
                message="No file path provided for upload.",
                execution_time=time.time() - start_time
            )

        res = self.manager.upload_file(selector, filepath)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=f"Uploaded file '{filepath}'",
            data=res.to_dict(),
            execution_time=elapsed
        )
