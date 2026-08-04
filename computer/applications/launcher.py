import asyncio
import logging
import os
import time
from typing import Any, List, Optional, Tuple

from computer.applications.models import ApplicationLaunchOptions, ApplicationState, AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Launcher")


class ApplicationLauncher:
    async def launch(self, options: ApplicationLaunchOptions) -> Tuple[bool, Optional[AURAApplication], str]:
        target = options.executable_or_name

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

            return (True, app, f"Launched '{app_name}' with PID {process.pid}")

        except FileNotFoundError:
            msg = f"Executable '{target}' not found"
            return (False, None, msg)
        except PermissionError:
            msg = f"Permission denied launching '{target}'"
            return (False, None, msg)
        except Exception as e:
            msg = f"Failed to launch '{target}': {str(e)}"
            return (False, None, msg)
