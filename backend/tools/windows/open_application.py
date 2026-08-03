import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class OpenApplicationTool(Tool):
    """Tool for launching Windows applications."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "open_application"

    @property
    def description(self) -> str:
        return "Launches a Windows application executable or standard system application."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        app_name = parameters.get("application") or parameters.get("app_name") or ""
        if not app_name:
            return ToolResult(
                success=False,
                message="No application specified in parameters.",
                execution_time=time.time() - start_time
            )

        res = self.manager.launch_app(app_name)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
