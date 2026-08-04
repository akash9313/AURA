import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from computer.windows.configuration import WindowManagerConfig
from computer.windows.events import WindowEvent
from computer.windows.models import (
    AURAWindow,
    WindowActionResult,
    WindowSearchQuery,
    WindowState,
)
from computer.windows.window_locator import WindowLocator
from computer.windows.window_monitor import WindowMonitor
from computer.windows.window_registry import WindowRegistry
from computer.windows.window_state import WindowStateTracker

logger = logging.getLogger("AURA.Computer.Windows.Manager")


class AURAWindowManager:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[WindowManagerConfig] = None,
    ):
        self.bus = bus
        self.config = config or WindowManagerConfig()

        self.registry = WindowRegistry(max_capacity=self.config.max_tracked_windows)
        self.locator = WindowLocator()
        self.state_tracker = WindowStateTracker()
        self.monitor = WindowMonitor(
            registry=self.registry,
            state_tracker=self.state_tracker,
            bus=bus,
            config=self.config,
        )

    def register_window(
        self,
        title: str,
        app_id: str = "desktop_app",
        bounds: Tuple[int, int, int, int] = (0, 0, 800, 600),
        process_id: int = 0,
        class_name: str = "",
        internal_handle: Optional[int] = None,
    ) -> AURAWindow:
        window = AURAWindow(
            title=title,
            app_id=app_id,
            bounds=bounds,
            process_id=process_id,
            class_name=class_name,
        )
        self.registry.register_window(window, internal_handle=internal_handle)
        self.monitor.notify_window_created(window)
        return window

    def enumerate_windows(self) -> List[AURAWindow]:
        return self.registry.get_all_windows()

    def get_active_window(self) -> Optional[AURAWindow]:
        return self.registry.get_active_window()

    def find_window(
        self,
        title: Optional[str] = None,
        app_name: Optional[str] = None,
        process_id: Optional[int] = None,
        regex_pattern: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> Optional[AURAWindow]:
        query = WindowSearchQuery(
            title=title,
            app_name=app_name,
            process_id=process_id,
            regex_pattern=regex_pattern,
            class_name=class_name,
            partial_match=True,
        )
        return self.locator.find_first_window(self.registry.get_all_windows(), query)

    def find_all_windows(
        self,
        title: Optional[str] = None,
        app_name: Optional[str] = None,
        process_id: Optional[int] = None,
        regex_pattern: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> List[AURAWindow]:
        query = WindowSearchQuery(
            title=title,
            app_name=app_name,
            process_id=process_id,
            regex_pattern=regex_pattern,
            class_name=class_name,
            partial_match=True,
        )
        return self.locator.find_windows(self.registry.get_all_windows(), query)

    async def focus_window(self, window_id: str) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "focus_window", f"Window '{window_id}' not found", start_time)

        self.monitor.notify_window_focused(win)
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="focus_window",
            message=f"Focused window '{win.title}'",
            state=WindowState.FOCUSED,
            execution_time_ms=duration,
        )

    async def minimize_window(self, window_id: str) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "minimize_window", f"Window '{window_id}' not found", start_time)

        self.state_tracker.set_minimized(win)
        self._publish_event(WindowEvent.WINDOW_MINIMIZED, win.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="minimize_window",
            message=f"Minimized window '{win.title}'",
            state=WindowState.MINIMIZED,
            execution_time_ms=duration,
        )

    async def maximize_window(self, window_id: str) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "maximize_window", f"Window '{window_id}' not found", start_time)

        self.state_tracker.set_maximized(win)
        self._publish_event(WindowEvent.WINDOW_MAXIMIZED, win.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="maximize_window",
            message=f"Maximized window '{win.title}'",
            state=WindowState.MAXIMIZED,
            execution_time_ms=duration,
        )

    async def restore_window(self, window_id: str) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "restore_window", f"Window '{window_id}' not found", start_time)

        self.state_tracker.set_normal(win)
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="restore_window",
            message=f"Restored window '{win.title}'",
            state=WindowState.NORMAL,
            execution_time_ms=duration,
        )

    async def move_window(self, window_id: str, x: int, y: int) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "move_window", f"Window '{window_id}' not found", start_time)

        _, _, w, h = win.bounds
        self.state_tracker.update_bounds(win, (x, y, w, h))
        self._publish_event(WindowEvent.WINDOW_MOVED, win.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="move_window",
            message=f"Moved window '{win.title}' to ({x}, {y})",
            state=win.state,
            execution_time_ms=duration,
        )

    async def resize_window(self, window_id: str, width: int, height: int) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "resize_window", f"Window '{window_id}' not found", start_time)

        x, y, _, _ = win.bounds
        self.state_tracker.update_bounds(win, (x, y, width, height))
        self._publish_event(WindowEvent.WINDOW_RESIZED, win.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="resize_window",
            message=f"Resized window '{win.title}' to ({width}x{height})",
            state=win.state,
            execution_time_ms=duration,
        )

    async def close_window(self, window_id: str) -> WindowActionResult:
        start_time = time.time()
        win = self.registry.get_window_by_id(window_id)
        if not win:
            return self._build_result(False, window_id, "close_window", f"Window '{window_id}' not found", start_time)

        self.state_tracker.set_closed(win)
        self.registry.unregister_window(window_id)
        self.monitor.notify_window_destroyed(window_id)
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=True,
            window_id=window_id,
            action="close_window",
            message=f"Closed window '{win.title}'",
            state=WindowState.CLOSED,
            execution_time_ms=duration,
        )

    async def bring_to_front(self, window_id: str) -> WindowActionResult:
        return await self.focus_window(window_id)

    def _build_result(self, success: bool, window_id: str, action: str, msg: str, start_time: float) -> WindowActionResult:
        duration = round((time.time() - start_time) * 1000, 2)
        return WindowActionResult(
            success=success,
            window_id=window_id,
            action=action,
            message=msg,
            execution_time_ms=duration,
        )

    def _publish_event(self, event: WindowEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish event '{event.value}': {e}")
