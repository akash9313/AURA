import logging
from typing import Any, Dict, List, Optional, Tuple

from core.service import Service
from computer.applications.application_manager import AURAApplicationManager
from computer.applications.configuration import ApplicationManagerConfig
from computer.applications.models import ApplicationResult, AURAApplication

logger = logging.getLogger("AURA.Computer.Applications.Service")


class ApplicationManagerService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[ApplicationManagerConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or ApplicationManagerConfig()
        self.manager = AURAApplicationManager(bus=bus, config=self.config)

    async def launch_app(
        self,
        executable_or_name: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        wait_ready: bool = True,
        timeout_ms: Optional[float] = None,
    ) -> Tuple[bool, Optional[AURAApplication], ApplicationResult]:
        return await self.manager.launch_app(
            executable_or_name=executable_or_name,
            args=args,
            cwd=cwd,
            env=env,
            wait_ready=wait_ready,
            timeout_ms=timeout_ms,
        )

    def find_app(self, name_or_id: str) -> Optional[AURAApplication]:
        return self.manager.find_app(name_or_id)

    def list_running_apps(self) -> List[AURAApplication]:
        return self.manager.list_running_apps()

    async def close_app(self, app_id: str, force: bool = False) -> ApplicationResult:
        return await self.manager.close_app(app_id, force=force)

    async def restart_app(self, app_id: str) -> Tuple[bool, Optional[AURAApplication], ApplicationResult]:
        return await self.manager.restart_app(app_id)

    async def wait_until_ready(self, app_id: str, timeout_ms: Optional[float] = None) -> bool:
        return await self.manager.wait_until_ready(app_id, timeout_ms=timeout_ms)

    def start(self) -> None:
        self.manager.monitor.start_monitoring()

    def stop(self) -> None:
        self.manager.monitor.stop_monitoring()

    def is_healthy(self) -> bool:
        return True
