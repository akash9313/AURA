import logging
import time
from typing import Optional, Tuple

from computer.windows.models import AURAWindow, WindowState

logger = logging.getLogger("AURA.Computer.Windows.State")


class WindowStateTracker:
    def set_focused(self, window: AURAWindow) -> None:
        window.state = WindowState.FOCUSED
        window.last_active_time = time.time()

    def set_minimized(self, window: AURAWindow) -> None:
        window.state = WindowState.MINIMIZED

    def set_maximized(self, window: AURAWindow) -> None:
        window.state = WindowState.MAXIMIZED
        window.last_active_time = time.time()

    def set_normal(self, window: AURAWindow) -> None:
        window.state = WindowState.NORMAL

    def set_hidden(self, window: AURAWindow) -> None:
        window.state = WindowState.HIDDEN
        window.is_visible = False

    def set_closed(self, window: AURAWindow) -> None:
        window.state = WindowState.CLOSED
        window.is_visible = False

    def update_bounds(self, window: AURAWindow, bounds: Tuple[int, int, int, int]) -> None:
        window.bounds = bounds
