"""
AURA Window Manager Subsystem.
Provides window discovery, tracking, search, focus, movement, spatial resizing, and state monitoring.
"""

from computer.windows.configuration import WindowManagerConfig
from computer.windows.events import WindowEvent
from computer.windows.models import (
    AURAWindow,
    WindowActionResult,
    WindowSearchQuery,
    WindowState,
)
from computer.windows.service import WindowManagerService
from computer.windows.window_locator import WindowLocator
from computer.windows.window_manager import AURAWindowManager
from computer.windows.window_monitor import WindowMonitor
from computer.windows.window_registry import WindowRegistry
from computer.windows.window_state import WindowStateTracker

__all__ = [
    "WindowManagerService",
    "AURAWindowManager",
    "WindowRegistry",
    "WindowLocator",
    "WindowStateTracker",
    "WindowMonitor",
    "WindowManagerConfig",
    "AURAWindow",
    "WindowState",
    "WindowSearchQuery",
    "WindowActionResult",
    "WindowEvent",
]
