import logging
import subprocess
import time
from typing import Optional
from developer.models import CommandResult

logger = logging.getLogger("AURA.Developer.Terminal")


class TerminalController:
    """
    Subprocess terminal command execution manager with output capture and error handling.
    """

    def run_command(self, command: str, cwd: Optional[str] = None, timeout: float = 60.0) -> CommandResult:
        """
        Execute terminal shell command synchronously.

        Args:
            command (str): Shell command string.
            cwd (str, optional): Working directory.
            timeout (float): Max execution time in seconds.

        Returns:
            CommandResult: Standardized execution result.
        """
        t0 = time.time()
        logger.info(f"Executing Terminal Command: '{command}' in '{cwd or '.'}'")

        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            dt = (time.time() - t0) * 1000.0
            return CommandResult(
                command=command,
                exit_code=res.returncode,
                stdout=res.stdout,
                stderr=res.stderr,
                execution_time_ms=dt
            )
        except subprocess.TimeoutExpired:
            dt = (time.time() - t0) * 1000.0
            logger.error(f"Terminal Command timed out after {timeout}s: '{command}'")
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Command execution timed out after {timeout} seconds.",
                execution_time_ms=dt
            )
        except Exception as e:
            dt = (time.time() - t0) * 1000.0
            return CommandResult(
                command=command,
                exit_code=1,
                stdout="",
                stderr=str(e),
                execution_time_ms=dt
            )
