"""
Computer Subsystem Domain Models.
Platform-independent data structures, enums, options, and results for desktop automation.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ComputerState(Enum):
    """Lifecycle state of the Computer Subsystem."""
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"


class PlatformType(Enum):
    """Supported operating system platforms."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    AUTO = "auto"


class DesktopActionType(Enum):
    """Desktop automation action primitives."""
    # Legacy Action Types
    OPEN_APP = "open_app"
    CLOSE_APP = "close_app"
    FOCUS_WINDOW = "focus_window"
    MOVE_WINDOW = "move_window"
    RESIZE_WINDOW = "resize_window"
    TYPE_TEXT = "type_text"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    MOUSE_CLICK = "mouse_click"
    DRAG_DROP = "drag_drop"
    CLIPBOARD_READ = "clipboard_read"
    CLIPBOARD_WRITE = "clipboard_write"
    EXPLORER_SEARCH = "explorer_search"
    SAVE_DIALOG = "save_dialog"

    # New Provider Action Types
    LAUNCH_APP = "launch_app"
    TERMINATE_APP = "terminate_app"
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    MOUSE_MOVE = "mouse_move"
    MOUSE_DRAG = "mouse_drag"
    PRESS_SHORTCUT = "press_shortcut"
    READ_CLIPBOARD = "read_clipboard"
    WRITE_CLIPBOARD = "write_clipboard"
    OPEN_FOLDER = "open_folder"
    FIND_UI_ELEMENT = "find_ui_element"
    CAPTURE_SCREEN = "capture_screen"


class SafetyLevel(Enum):
    """Safety classification levels for desktop automation actions."""
    SAFE = "safe"
    NORMAL = "normal"
    SENSITIVE = "sensitive"
    DANGEROUS = "dangerous"


# Legacy alias for ActionType
ActionType = DesktopActionType


@dataclass
class DesktopWindowInfo:
    """Platform-independent window handle details."""
    handle: int
    title: str
    class_name: str
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    is_focused: bool = False
    is_minimized: bool = False
    is_maximized: bool = False
    pid: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "handle": self.handle,
            "title": self.title,
            "class_name": self.class_name,
            "bounds": self.bounds,
            "is_focused": self.is_focused,
            "is_minimized": self.is_minimized,
            "is_maximized": self.is_maximized,
            "pid": self.pid,
        }


# Legacy WindowInfo alias
WindowInfo = DesktopWindowInfo


@dataclass
class DesktopAppInfo:
    """Running desktop process metadata."""
    pid: int
    name: str
    executable_path: str
    windows: List[DesktopWindowInfo] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "executable_path": self.executable_path,
            "window_count": len(self.windows),
        }


# Legacy AppInfo alias
AppInfo = DesktopAppInfo


@dataclass
class DesktopUIElement:
    """Platform-independent UI Automation element representation."""
    automation_id: str
    name: str
    control_type: str
    bounds: Tuple[int, int, int, int]
    is_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "automation_id": self.automation_id,
            "name": self.name,
            "control_type": self.control_type,
            "bounds": self.bounds,
            "is_enabled": self.is_enabled,
        }


# Legacy UIElement alias
UIElement = DesktopUIElement


@dataclass
class ClipboardContent:
    """Captured clipboard payload."""
    text: Optional[str] = None
    formats: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "formats": self.formats,
            "timestamp": self.timestamp,
        }


@dataclass
class ComputerResult:
    """Unified result of a desktop automation action."""
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "action": self.action,
            "message": self.message,
            "data": self.data or {},
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }


# Legacy AutomationResult alias
AutomationResult = ComputerResult


@dataclass
class ComputerHealthStatus:
    """Health telemetry metrics for the Computer Subsystem."""
    state: ComputerState
    platform: PlatformType
    provider_name: str
    total_actions: int
    successful_actions: int
    failed_actions: int
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "platform": self.platform.value,
            "provider_name": self.provider_name,
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "last_error": self.last_error,
        }
