import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger("AURA.Developer.Debugger")


class ExceptionDebugger:
    """
    Parses stack traces, explains exceptions, locates fault lines, and suggests fixes.
    """

    def analyze_stack_trace(self, stack_trace: str) -> Dict[str, str]:
        if not stack_trace.strip():
            return {"error_type": "Unknown", "message": "No stack trace provided", "suggestion": "Provide valid stderr logs."}

        # Match Python Tracebacks
        py_match = re.findall(r'File "([^"]+)", line (\d+), in (\w+)\n\s*(.+)\n(\w+Error|\w+Exception): (.+)', stack_trace)
        if py_match:
            file_path, line_no, func, code_snippet, err_type, err_msg = py_match[-1]
            return {
                "file": file_path,
                "line": line_no,
                "function": func,
                "error_type": err_type,
                "message": err_msg,
                "suggestion": f"Check line {line_no} in {file_path} for invalid parameters or missing variable initialization."
            }

        return {
            "error_type": "Runtime Error",
            "message": stack_trace[:200],
            "suggestion": "Inspect log snippet for syntax errors or unmet precondition assumptions."
        }
