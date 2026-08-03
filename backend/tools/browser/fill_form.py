import time
from typing import Any, Dict
from browser.manager import BrowserManager
from tools.base import Tool
from tools.result import ToolResult


class FillFormTool(Tool):
    """Tool for filling web forms."""

    def __init__(self, manager: BrowserManager = None):
        self.manager = manager if manager is not None else BrowserManager()

    @property
    def name(self) -> str:
        return "fill_form"

    @property
    def description(self) -> str:
        return "Fills web form input elements with specified data."

    @property
    def category(self) -> str:
        return "browser"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        form_data = parameters.get("form_data") or parameters.get("fields") or {}

        if not form_data:
            return ToolResult(
                success=False,
                message="No form data provided to fill.",
                execution_time=time.time() - start_time
            )

        res = self.manager.fill_form(form_data)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message="Web form filled.",
            data=res.to_dict(),
            execution_time=elapsed
        )
