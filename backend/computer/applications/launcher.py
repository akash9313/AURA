"""
Application Launcher Engine.
Asynchronously launches executables and application names with arguments, working directory, and environment overrides.
Encapsulates process spawning and handles launch errors cleanly.
"""

import asyncio
import logging
import os
import time
from typing import Any, List, Optional, Tuple

from computer.applications.models import ApplicationLaunchOptions, ApplicationState, AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Launcher")


class ApplicationLauncher:
    """
    Spawns desktop application processes and builds AURAApplication domain objects.
    """

    async def launch(self, options: ApplicationLaunchOptions) -> Tuple[bool, Optional[AURAApplication], str]:
        """
        Asynchronously launch target desktop application.

        Args:
            options: ApplicationLaunchOptions specifications.

        Returns:
            Tuple of (success, AURAApplication, status_message)
        """
        target = options.executable_or_name
        logger.info(f"Launching application target '{target}' with args {options.args}...")

        try:
            cmd = [target] + options.args
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=options.cwd,
                env=options.env or os.environ.copy(),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            app_name = os.path.basename(target)
            app = AURAApplication(
                name=app_name,
                executable_path=target,
                process_id=process.pid,
                status=ApplicationState.STARTING,
                working_directory=options.cwd or os.getcwd(),
                command_line=cmd,
                _internal_process_ref=process,
            )

            logger.info(f"Successfully launched '{app_name}' (PID: {process.pid})")
            return (True, app, f"Launched '{app_name}' with PID {process.pid}")

        except FileNotFoundError:
            msg = f"Executable '{target}' not found"
            logger.error(msg)
            return (False, None, msg)
        except PermissionError:
            msg = f"Permission denied launching '{target}'"
            logger.error(msg)
            return (False, None, msg)
        except Exception as e:
            msg = f"Failed to launch '{target}': {str(e)}"
            logger.error(msg)
            return (False, None, msg)
