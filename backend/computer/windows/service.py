"""
Window Manager Service.
Top-level AURA service integrating the AURAWindowManager into the kernel framework.
Exposes platform-independent interfaces for discovering, searching, focusing, moving, and controlling desktop windows.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from core.service import Service
from computer.windows.configuration import WindowManagerConfig
from computer.windows.models import AURAWindow, WindowActionResult, WindowState
from computer.windows.window_manager import AURAWindowManager

logger = logging.getLogger("AURA.Computer.Windows.Service")


class WindowManagerService(Service):
    """
    Service wrapper exposing Window Manager operations to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[WindowManagerConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or WindowManagerConfig()
        self.manager = AURAWindowManager(bus=bus, config=self.config)
        logger.info("WindowManagerService initialized")

    def register_window(
        self,
        title: str,
        app_id: str = "desktop_app",
        bounds: Tuple[int, int, int, int] = (0, 0, 800, 600),
        process_id: int = 0,
        class_name: str = "",
    ) -> AURAWindow:
        """Register a discovered desktop window."""
        return self.manager.register_window(
            title=title, app_id=app_id, bounds=bounds, process_id=process_id, class_name=class_name
        )

    def enumerate_windows(self) -> List[AURAWindow]:
        """List all tracked windows."""
        return self.manager.enumerate_windows()

    def get_active_window(self) -> Optional[AURAWindow]:
        """Get current foreground window."""
        return self.manager.get_active_window()

    def find_window(
        self,
        title: Optional[str] = None,
        app_name: Optional[str] = None,
        process_id: Optional[int] = None,
        regex_pattern: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> Optional[AURAWindow]:
        """Search first window matching criteria."""
        return self.manager.find_window(
            title=title, app_name=app_name, process_id=process_id, regex_pattern=regex_pattern, class_name=class_name
        )

    async def focus_window(self, window_id: str) -> WindowActionResult:
        """Focus window by ID."""
        return await self.manager.focus_window(window_id)

    async def minimize_window(self, window_id: str) -> WindowActionResult:
        """Minimize window by ID."""
        return await self.manager.minimize_window(window_id)

    async def maximize_window(self, window_id: str) -> WindowActionResult:
        """Maximize window by ID."""
        return await self.manager.maximize_window(window_id)

    async def restore_window(self, window_id: str) -> WindowActionResult:
        """Restore window by ID."""
        return await self.manager.restore_window(window_id)

    async def move_window(self, window_id: str, x: int, y: int) -> WindowActionResult:
        """Move window by ID."""
        return await self.manager.move_window(window_id, x, y)

    async def resize_window(self, window_id: str, width: int, height: int) -> WindowActionResult:
        """Resize window by ID."""
        return await self.manager.resize_window(window_id, width, height)

    async def close_window(self, window_id: str) -> WindowActionResult:
        """Close window by ID."""
        return await self.manager.close_window(window_id)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting WindowManagerService...")
        self.manager.monitor.start_monitoring()

    def stop(self) -> None:
        logger.info("Stopping WindowManagerService...")
        self.manager.monitor.stop_monitoring()

    def is_healthy(self) -> bool:
        return True
