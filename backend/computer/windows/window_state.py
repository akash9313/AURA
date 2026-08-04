"""
Window State Tracker.
Tracks state transitions (focused, minimized, maximized, hidden, closed) and spatial bounds for AURAWindow instances.
"""

import logging
import time
from typing import Optional, Tuple

from computer.windows.models import AURAWindow, WindowState

logger = logging.getLogger("AURA.Computer.Windows.State")


class WindowStateTracker:
    """
    Manages and validates WindowState transitions for AURAWindow domain objects.
    """

    def set_focused(self, window: AURAWindow) -> None:
        """Mark window as focused."""
        window.state = WindowState.FOCUSED
        window.last_active_time = time.time()
        logger.debug(f"Window '{window.window_id}' state -> FOCUSED")

    def set_minimized(self, window: AURAWindow) -> None:
        """Mark window as minimized."""
        window.state = WindowState.MINIMIZED
        logger.debug(f"Window '{window.window_id}' state -> MINIMIZED")

    def set_maximized(self, window: AURAWindow) -> None:
        """Mark window as maximized."""
        window.state = WindowState.MAXIMIZED
        window.last_active_time = time.time()
        logger.debug(f"Window '{window.window_id}' state -> MAXIMIZED")

    def set_normal(self, window: AURAWindow) -> None:
        """Mark window as normal."""
        window.state = WindowState.NORMAL
        logger.debug(f"Window '{window.window_id}' state -> NORMAL")

    def set_hidden(self, window: AURAWindow) -> None:
        """Mark window as hidden."""
        window.state = WindowState.HIDDEN
        window.is_visible = False
        logger.debug(f"Window '{window.window_id}' state -> HIDDEN")

    def set_closed(self, window: AURAWindow) -> None:
        """Mark window as closed."""
        window.state = WindowState.CLOSED
        window.is_visible = False
        logger.debug(f"Window '{window.window_id}' state -> CLOSED")

    def update_bounds(self, window: AURAWindow, bounds: Tuple[int, int, int, int]) -> None:
        """Update window coordinate bounds."""
        window.bounds = bounds
        logger.debug(f"Window '{window.window_id}' bounds updated: {bounds}")
