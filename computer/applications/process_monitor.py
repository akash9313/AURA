import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from computer.applications.configuration import ApplicationManagerConfig
from computer.applications.events import ApplicationEvent
from computer.applications.lifecycle import ApplicationLifecycleTracker
from computer.applications.models import ApplicationState, AURAApplication
from computer.applications.registry import ApplicationRegistry

logger = logging.getLogger("AURA.Computer.Applications.Monitor")


class ProcessMonitor:
    def __init__(
        self,
        registry: ApplicationRegistry,
        lifecycle: ApplicationLifecycleTracker,
        bus: Any = None,
        config: Optional[ApplicationManagerConfig] = None,
    ):
        self.registry = registry
        self.lifecycle = lifecycle
        self.bus = bus
        self.config = config or ApplicationManagerConfig()

        self._running: bool = False
        self._monitor_task: Optional[asyncio.Task] = None

    def start_monitoring(self) -> None:
        if not self._running and self.config.enable_process_monitoring:
            self._running = True
            try:
                loop = asyncio.get_running_loop()
                self._monitor_task = loop.create_task(self._monitor_loop())
            except RuntimeError:
                pass

    def stop_monitoring(self) -> None:
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None

    async def _monitor_loop(self) -> None:
        while self._running:
            try:
                await self.audit_resources()
            except Exception as e:
                logger.warning(f"ProcessMonitor audit error: {e}")

            interval_sec = self.config.resource_poll_interval_ms / 1000.0
            await asyncio.sleep(interval_sec)

    async def audit_resources(self) -> None:
        for app in self.registry.get_all_apps():
            if app.status in (ApplicationState.CLOSED, ApplicationState.CRASHED):
                continue

            if app._internal_process_ref and hasattr(app._internal_process_ref, "returncode"):
                code = app._internal_process_ref.returncode
                if code is not None:
                    if code == 0:
                        self.lifecycle.set_closed(app)
                        self._publish_event(ApplicationEvent.APPLICATION_CLOSED, app.to_dict())
                    else:
                        self.lifecycle.set_crashed(app)
                        self._publish_event(ApplicationEvent.APPLICATION_CRASHED, app.to_dict())

            self._publish_event(ApplicationEvent.RESOURCE_UPDATED, app.to_dict())

    def _publish_event(self, event: ApplicationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish application event '{event.value}': {e}")
