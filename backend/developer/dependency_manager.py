import logging
import os
from typing import List, Optional
from developer.models import TechStack
from developer.terminal import TerminalController

logger = logging.getLogger("AURA.Developer.DependencyManager")


class DependencyManager:
    """
    Detects and installs package dependencies across Node, Python, Rust, Go, etc.
    """

    def __init__(self, terminal: Optional[TerminalController] = None):
        self.terminal = terminal if terminal is not None else TerminalController()

    def install_dependencies(self, project_path: str, tech_stack: TechStack) -> bool:
        """
        Install package dependencies based on tech stack.
        """
        if tech_stack in (TechStack.JAVASCRIPT, TechStack.TYPESCRIPT):
            if os.path.exists(os.path.join(project_path, "package.json")):
                res = self.terminal.run_command("npm install", cwd=project_path)
                return res.is_success()
        elif tech_stack == TechStack.PYTHON:
            if os.path.exists(os.path.join(project_path, "requirements.txt")):
                res = self.terminal.run_command("pip install -r requirements.txt", cwd=project_path)
                return res.is_success()
        return True
