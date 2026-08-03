import logging
from typing import Optional
from developer.models import CommandResult
from developer.terminal import TerminalController

logger = logging.getLogger("AURA.Developer.VSCode")


class VSCodeController:
    """
    VS Code workspace and editor controller via shell CLI ('code').
    """

    def __init__(self, terminal: Optional[TerminalController] = None):
        self.terminal = terminal if terminal is not None else TerminalController()

    def open_workspace(self, path: str) -> CommandResult:
        return self.terminal.run_command(f'code "{path}"')

    def open_file(self, file_path: str, line_number: Optional[int] = None) -> CommandResult:
        cmd = f'code -g "{file_path}:{line_number}"' if line_number else f'code "{file_path}"'
        return self.terminal.run_command(cmd)
