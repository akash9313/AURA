import logging
from typing import Any, Dict, List, Optional, Tuple

from core.service import Service
from computer.windows.configuration import WindowManagerConfig
from computer.windows.models import AURAWindow, WindowActionResult, WindowState
from computer.windows.window_manager import AURAWindowManager

logger = logging.getLogger("AURA.Computer.Windows.Service")


class WindowManagerService(Service):
    def __init__(
        self,
        bus: Any = None,
        config: Optional[WindowManagerConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or WindowManagerConfig()
        self.manager = AURAWindowManager(bus=bus, config=self.config)

    def register_window(
        self,
        title: str,
        app_id: str = "desktop_app",
        bounds: Tuple[int, int, int, int] = (0, 0, 800, 600),
        process_id: int = 0,
        class_name: str = "",
    ) -> AURAWindow:
        return self.manager.register_window(
            title=title, app_id=app_id, bounds=bounds, process_id=process_id, class_name=class_name
        )

    def enumerate_windows(self) -> List[AURAWindow]:
        return self.manager.enumerate_windows()

    def get_active_window(self) -> Optional[AURAWindow]:
        return self.manager.get_active_window()

    def find_window(
        self,
        title: Optional[str] = None,
        app_name: Optional[str] = None,
        process_id: Optional[int] = None,
        regex_pattern: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> Optional[AURAWindow]:
        return self.manager.find_window(
            title=title, app_name=app_name, process_id=process_id, regex_pattern=regex_pattern, class_name=class_name
        )

    async def focus_window(self, window_id: str) -> WindowActionResult:
        return await self.manager.focus_window(window_id)

    async def minimize_window(self, window_id: str) -> WindowActionResult:
        return await self.manager.minimize_window(window_id)

    async def maximize_window(self, window_id: str) -> WindowActionResult:
        return await self.manager.maximize_window(window_id)

    async def restore_window(self, window_id: str) -> WindowActionResult:
        return await self.manager.restore_window(window_id)

    async def move_window(self, window_id: str, x: int, y: int) -> WindowActionResult:
        return await self.manager.move_window(window_id, x, y)

    async def resize_window(self, window_id: str, width: int, height: int) -> WindowActionResult:
        return await self.manager.resize_window(window_id, width, height)

    async def close_window(self, window_id: str) -> WindowActionResult:
        return await self.manager.close_window(window_id)

    def start(self) -> None:
        self.manager.monitor.start_monitoring()

    def stop(self) -> None:
        self.manager.monitor.stop_monitoring()

    def is_healthy(self) -> bool:
        return True
