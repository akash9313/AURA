import logging
import os
from typing import Optional
from developer.models import TechStack, TestResultSummary
from developer.terminal import TerminalController

logger = logging.getLogger("AURA.Developer.Testing")


class TestRunner:
    """
    Test suite execution manager supporting Pytest, Unittest, Jest/npm test, etc.
    """

    def __init__(self, terminal: Optional[TerminalController] = None):
        self.terminal = terminal if terminal is not None else TerminalController()

    def run_tests(self, project_path: str, tech_stack: TechStack) -> TestResultSummary:
        if tech_stack == TechStack.PYTHON:
            cmd = "python -m unittest discover -s tests" if os.path.exists(os.path.join(project_path, "tests")) else "pytest"
        elif tech_stack in (TechStack.JAVASCRIPT, TechStack.TYPESCRIPT):
            cmd = "npm test"
        else:
            cmd = "python -m unittest"

        res = self.terminal.run_command(cmd, cwd=project_path)

        if res.is_success():
            return TestResultSummary(total_tests=1, passed_tests=1, failed_tests=0, skipped_tests=0, execution_time_ms=res.execution_time_ms)
        else:
            return TestResultSummary(
                total_tests=1,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                failure_details=[{"command": cmd, "stderr": res.stderr or res.stdout}],
                execution_time_ms=res.execution_time_ms
            )
