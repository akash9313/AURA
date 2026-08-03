import logging
from typing import Dict, List, Optional
from developer.models import CommandResult, RepositoryStatus
from developer.terminal import TerminalController

logger = logging.getLogger("AURA.Developer.Git")


class GitManager:
    """
    Git repository automation with status inspection and action execution.
    """

    def __init__(self, terminal: Optional[TerminalController] = None):
        self.terminal = terminal if terminal is not None else TerminalController()

    def get_status(self, repo_path: str) -> RepositoryStatus:
        res = self.terminal.run_command("git status --porcelain -b", cwd=repo_path)
        if not res.is_success():
            return RepositoryStatus(branch="unknown", is_clean=True)

        lines = res.stdout.strip().split("\n")
        branch = "main"
        modified = []
        untracked = []

        for line in lines:
            if line.startswith("##"):
                branch = line[3:].split("...")[0].strip()
            elif line.startswith(" M") or line.startswith("M "):
                modified.append(line[3:].strip())
            elif line.startswith("??"):
                untracked.append(line[3:].strip())

        is_clean = (len(modified) == 0 and len(untracked) == 0)
        return RepositoryStatus(branch=branch, is_clean=is_clean, modified_files=modified, untracked_files=untracked)

    def commit(self, repo_path: str, message: str) -> CommandResult:
        self.terminal.run_command("git add .", cwd=repo_path)
        return self.terminal.run_command(f'git commit -m "{message}"', cwd=repo_path)
