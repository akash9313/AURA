"""
Window Subsystem Health & Lifecycle Monitor.
Continuously audits active foreground windows, bounds changes, and window lifecycle creation/destruction.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from computer.windows.configuration import WindowManagerConfig
from computer.windows.events import WindowEvent
from computer.windows.models import AURAWindow, WindowState
from computer.windows.window_registry import WindowRegistry
from computer.windows.window_state import WindowStateTracker

logger = logging.getLogger("AURA.Computer.Windows.Monitor")


class WindowMonitor:
    """
    Active background monitor tracking window state mutations and publishing events to EventBus.
    """

    def __init__(
        self,
        registry: WindowRegistry,
        state_tracker: WindowStateTracker,
        bus: Any = None,
        config: Optional[WindowManagerConfig] = None,
    ):
        self.registry = registry
        self.state_tracker = state_tracker
        self.bus = bus
        self.config = config or WindowManagerConfig()

        self._running: bool = False
        self._monitor_task: Optional[asyncio.Task] = None

    def start_monitoring(self) -> None:
        """Start async background monitor loop."""
        if not self._running:
            self._running = True
            try:
                loop = asyncio.get_running_loop()
                self._monitor_task = loop.create_task(self._monitor_loop())
                logger.info("WindowMonitor loop started")
            except RuntimeError:
                logger.debug("No active loop for WindowMonitor. Manual check mode active.")

    def stop_monitoring(self) -> None:
        """Stop background monitor loop."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
            logger.info("WindowMonitor loop stopped")

    async def _monitor_loop(self) -> None:
        """Periodic polling loop monitoring window changes."""
        while self._running:
            try:
                await self.audit_windows()
            except Exception as e:
                logger.warning(f"WindowMonitor audit error: {e}")

            interval_sec = self.config.polling_interval_ms / 1000.0
            await asyncio.sleep(interval_sec)

    async def audit_windows(self) -> None:
        """Single audit pass over registered windows."""
        all_windows = self.registry.get_all_windows()
        for win in all_windows:
            if win.state == WindowState.CLOSED:
                self._publish_event(WindowEvent.WINDOW_CLOSED, win.to_dict())

    def notify_window_created(self, window: AURAWindow) -> None:
        """Emit WINDOW_CREATED event."""
        self._publish_event(WindowEvent.WINDOW_CREATED, window.to_dict())

    def notify_window_destroyed(self, window_id: str) -> None:
        """Emit WINDOW_DESTROYED event."""
        self._publish_event(WindowEvent.WINDOW_DESTROYED, {"window_id": window_id})

    def notify_window_focused(self, window: AURAWindow) -> None:
        """Emit WINDOW_FOCUSED event."""
        self.state_tracker.set_focused(window)
        self.registry.set_active_window_id(window.window_id)
        self._publish_event(WindowEvent.WINDOW_FOCUSED, window.to_dict())

    def _publish_event(self, event: WindowEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish window event '{event.value}': {e}")
