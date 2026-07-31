import logging
import subprocess
import time
from typing import Dict, Any
from tools.base import Tool
from tools.result import ToolResult

logger = logging.getLogger("AURA.Tools.Windows.OpenApplication")


class OpenApplicationTool(Tool):
    """
    Tool to launch desktop applications on Windows.
    
    Supported applications include Notepad, Calculator, Chrome, or specific executable shortcuts.
    """

    APP_MAP = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe"
    }

    @property
    def name(self) -> str:
        return "open_application"

    @property
    def description(self) -> str:
        return "Opens supported Windows applications such as Chrome, Notepad, or Calculator."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute application launch command.

        Args:
            parameters (dict): Expected key 'application' or 'app' (e.g. 'notepad', 'chrome', 'calculator').

        Returns:
            ToolResult: Status of the launch attempt.
        """
        start_time = time.time()
        app_name = parameters.get("application") or parameters.get("app") or ""
        app_key = str(app_name).strip().lower()

        if not app_key:
            elapsed = time.time() - start_time
            logger.warning("OpenApplicationTool executed without specifying an application.")
            return ToolResult(
                success=False,
                message="No application specified in parameters.",
                execution_time=elapsed
            )

        executable = self.APP_MAP.get(app_key)

        if not executable:
            elapsed = time.time() - start_time
            logger.warning(f"Application '{app_name}' is not supported.")
            return ToolResult(
                success=False,
                message=f"Application '{app_name}' is not supported.",
                data={"requested_app": app_name},
                execution_time=elapsed
            )

        try:
            logger.info(f"Launching desktop application: '{app_name}' using executable '{executable}'")
            subprocess.Popen(executable)
            elapsed = time.time() - start_time
            display_name = app_key.title()
            return ToolResult(
                success=True,
                message=f"{display_name} opened.",
                data={"application": app_name, "executable": executable},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed to launch application '{app_name}': {e}")
            return ToolResult(
                success=False,
                message=f"Failed to launch application '{app_name}': {e}",
                data={"application": app_name, "error": str(e)},
                execution_time=elapsed
            )
