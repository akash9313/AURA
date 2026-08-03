import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class CloseApplicationTool(Tool):
    """Tool for closing running Windows applications."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "close_application"

    @property
    def description(self) -> str:
        return "Terminates running process matching application name."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        app_name = parameters.get("application") or parameters.get("app_name") or ""
        if not app_name:
            return ToolResult(
                success=False,
                message="No application specified to close.",
                execution_time=time.time() - start_time
            )

        res = self.manager.close_app(app_name)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
