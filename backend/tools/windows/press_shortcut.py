import time
from typing import Any, Dict, List
from tools.base import Tool
from tools.result import ToolResult
from windows.manager import WindowsAutomationManager


class PressShortcutTool(Tool):
    """Tool for pressing keyboard hotkeys and shortcuts."""

    def __init__(self, manager: WindowsAutomationManager = None):
        self.manager = manager if manager is not None else WindowsAutomationManager()

    @property
    def name(self) -> str:
        return "press_shortcut"

    @property
    def description(self) -> str:
        return "Executes key combination shortcut (e.g. ['ctrl', 'c'] or ['alt', 'tab'])."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        keys = parameters.get("keys") or []
        if isinstance(keys, str):
            keys = [k.strip() for k in keys.split("+")]

        if not keys:
            return ToolResult(
                success=False,
                message="No shortcut keys specified.",
                execution_time=time.time() - start_time
            )

        res = self.manager.press_shortcut(keys)
        elapsed = time.time() - start_time

        return ToolResult(
            success=res.success,
            message=res.message,
            data=res.data,
            execution_time=elapsed
        )
