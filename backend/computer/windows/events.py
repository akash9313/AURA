"""
Window Subsystem Event Definitions.
Emitted to EventBus when window lifecycle or state changes occur.
"""

from enum import Enum


class WindowEvent(Enum):
    """Event definitions for Window Manager Subsystem."""
    WINDOW_CREATED = "window_created"
    WINDOW_DESTROYED = "window_destroyed"
    WINDOW_FOCUSED = "window_focused"
    WINDOW_MOVED = "window_moved"
    WINDOW_RESIZED = "window_resized"
    WINDOW_MINIMIZED = "window_minimized"
    WINDOW_MAXIMIZED = "window_maximized"
    WINDOW_CLOSED = "window_closed"
