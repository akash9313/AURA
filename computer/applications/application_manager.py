import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from computer.applications.configuration import ApplicationManagerConfig
from computer.applications.events import ApplicationEvent
from computer.applications.launcher import ApplicationLauncher
from computer.applications.lifecycle import ApplicationLifecycleTracker
from computer.applications.models import (
    ApplicationLaunchOptions,
    ApplicationResult,
    ApplicationState,
    AURAApplication,
)
from computer.applications.process_monitor import ProcessMonitor
from computer.applications.registry import ApplicationRegistry

logger = logging.getLogger("AURA.Computer.Applications.Manager")


class AURAApplicationManager:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[ApplicationManagerConfig] = None,
    ):
        self.bus = bus
        self.config = config or ApplicationManagerConfig()

        self.registry = ApplicationRegistry()
        self.lifecycle = ApplicationLifecycleTracker()
        self.launcher = ApplicationLauncher()
        self.monitor = ProcessMonitor(
            registry=self.registry,
            lifecycle=self.lifecycle,
            bus=bus,
            config=self.config,
        )

    async def launch_app(
        self,
        executable_or_name: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        wait_ready: bool = True,
        timeout_ms: Optional[float] = None,
    ) -> Tuple[bool, Optional[AURAApplication], ApplicationResult]:
        start_time = time.time()
        options = ApplicationLaunchOptions(
            executable_or_name=executable_or_name,
            args=args or [],
            cwd=cwd,
            env=env,
            wait_ready=wait_ready,
            timeout_ms=timeout_ms if timeout_ms is not None else self.config.launch_timeout_ms,
        )

        ok, app, msg = await self.launcher.launch(options)
        if not ok or not app:
            res = self._build_result(False, "none", "launch_app", msg, start_time)
            self._publish_event(ApplicationEvent.APPLICATION_NOT_FOUND, {"target": executable_or_name, "error": msg})
            return (False, None, res)

        self.registry.register_app(app, internal_process_ref=app._internal_process_ref)
        self._publish_event(ApplicationEvent.APPLICATION_LAUNCHED, app.to_dict())

        if wait_ready:
            await self.wait_until_ready(app.app_id, timeout_ms=options.timeout_ms)

        duration = round((time.time() - start_time) * 1000, 2)
        res = ApplicationResult(
            success=True,
            app_id=app.app_id,
            action="launch_app",
            message=f"Application '{app.name}' launched successfully",
            data=app.to_dict(),
            execution_time_ms=duration,
        )
        return (True, app, res)

    async def wait_until_ready(self, app_id: str, timeout_ms: Optional[float] = None) -> bool:
        app = self.registry.get_app_by_id(app_id)
        if not app:
            return False

        timeout_sec = (timeout_ms if timeout_ms is not None else self.config.readiness_timeout_ms) / 1000.0
        start_time = time.time()

        while time.time() - start_time <= timeout_sec:
            if app.process_id > 0:
                self.lifecycle.set_ready(app)
                self._publish_event(ApplicationEvent.APPLICATION_READY, app.to_dict())
                return True
            await asyncio.sleep(0.1)

        return False

    def find_app(self, name_or_id: str) -> Optional[AURAApplication]:
        app = self.registry.get_app_by_id(name_or_id)
        if not app:
            app = self.registry.get_app_by_name(name_or_id)
        return app

    def list_running_apps(self) -> List[AURAApplication]:
        return [app for app in self.registry.get_all_apps() if app.status != ApplicationState.CLOSED]

    async def close_app(self, app_id: str, force: bool = False) -> ApplicationResult:
        start_time = time.time()
        app = self.registry.get_app_by_id(app_id)
        if not app:
            return self._build_result(False, app_id, "close_app", f"Application '{app_id}' not found", start_time)

        self.lifecycle.set_closed(app)

        if app._internal_process_ref and hasattr(app._internal_process_ref, "terminate"):
            try:
                if force:
                    app._internal_process_ref.kill()
                else:
                    app._internal_process_ref.terminate()
            except Exception as e:
                logger.warning(f"Process termination warning for '{app_id}': {e}")

        self.registry.unregister_app(app_id)
        self._publish_event(ApplicationEvent.APPLICATION_CLOSED, app.to_dict())

        duration = round((time.time() - start_time) * 1000, 2)
        return ApplicationResult(
            success=True,
            app_id=app_id,
            action="close_app",
            message=f"Application '{app.name}' closed",
            execution_time_ms=duration,
        )

    async def restart_app(self, app_id: str) -> Tuple[bool, Optional[AURAApplication], ApplicationResult]:
        start_time = time.time()
        app = self.registry.get_app_by_id(app_id)
        if not app:
            res = self._build_result(False, app_id, "restart_app", f"Application '{app_id}' not found", start_time)
            return (False, None, res)

        exe = app.executable_path
        args = app.command_line[1:] if len(app.command_line) > 1 else []
        cwd = app.working_directory

        await self.close_app(app_id, force=True)
        ok, new_app, res = await self.launch_app(exe, args=args, cwd=cwd)

        if ok and new_app:
            self._publish_event(ApplicationEvent.APPLICATION_RESTARTED, new_app.to_dict())

        return (ok, new_app, res)

    def _build_result(self, success: bool, app_id: str, action: str, msg: str, start_time: float) -> ApplicationResult:
        duration = round((time.time() - start_time) * 1000, 2)
        return ApplicationResult(
            success=success,
            app_id=app_id,
            action=action,
            message=msg,
            execution_time_ms=duration,
        )

    def _publish_event(self, event: ApplicationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish event '{event.value}': {e}")
