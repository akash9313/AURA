import logging
import subprocess
import time
from typing import Dict, Any
from tools.base import Tool
from tools.result import ToolResult

logger = logging.getLogger("AURA.Tools.Windows.Calculator")


class CalculatorTool(Tool):
    """
    Tool to open the Windows Calculator or execute mathematical calculations.
    """

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Launches Windows Calculator or calculates mathematical expressions."

    @property
    def category(self) -> str:
        return "windows"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute Calculator tool.

        If an 'expression' parameter is supplied, evaluates the math expression.
        Otherwise, launches the Windows Calculator desktop app.

        Args:
            parameters (dict): Optional key 'expression' (e.g. '2 + 2').

        Returns:
            ToolResult: Calculation result or launch status.
        """
        start_time = time.time()
        expression = parameters.get("expression")

        if expression:
            try:
                # Safe math expression evaluation
                allowed_chars = set("0123456789+-*/(). ")
                if not set(str(expression)).issubset(allowed_chars):
                    raise ValueError("Expression contains invalid characters.")
                
                res = eval(str(expression), {"__builtins__": None}, {})
                elapsed = time.time() - start_time
                logger.info(f"Evaluated expression '{expression}' = {res}")
                return ToolResult(
                    success=True,
                    message=f"Result: {res}",
                    data={"expression": expression, "result": res},
                    execution_time=elapsed
                )
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Calculation error for '{expression}': {e}")
                return ToolResult(
                    success=False,
                    message=f"Calculation error: {e}",
                    data={"expression": expression, "error": str(e)},
                    execution_time=elapsed
                )

        # Launch Windows Calculator application
        try:
            logger.info("Launching Windows Calculator application...")
            subprocess.Popen("calc.exe")
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message="Calculator opened.",
                data={"application": "calculator", "executable": "calc.exe"},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed to launch Calculator: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to launch Calculator: {e}",
                data={"error": str(e)},
                execution_time=elapsed
            )
