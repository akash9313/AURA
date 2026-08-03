from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import time


class SafetyLevel(Enum):
    """Safety classification levels for desktop automation actions."""
    SAFE = "safe"          # Read-only screen/window queries
    NORMAL = "normal"      # Standard non-destructive app launches and typing
    SENSITIVE = "sensitive" # File modifications, deletions, file overwrites
    DANGEROUS = "dangerous" # System shutdowns, formatting, high-risk admin commands


class ActionType(Enum):
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


@dataclass
class WindowInfo:
    """Represents a desktop application window."""
    hwnd: int
    title: str
    class_name: str
    bounds: Tuple[int, int, int, int]  # x, y, width, height
    is_focused: bool = False
    is_minimized: bool = False
    is_maximized: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hwnd": self.hwnd,
            "title": self.title,
            "class_name": self.class_name,
            "bounds": self.bounds,
            "is_focused": self.is_focused,
            "is_minimized": self.is_minimized,
            "is_maximized": self.is_maximized,
        }


@dataclass
class AppInfo:
    """Represents a running desktop process/application."""
    pid: int
    name: str
    executable_path: str
    windows: List[WindowInfo] = field(default_factory=list)


@dataclass
class UIElement:
    """Represents a UI Automation element node."""
    automation_id: str
    name: str
    control_type: str
    bounds: Tuple[int, int, int, int]
    is_enabled: bool = True


@dataclass
class AutomationResult:
    """Execution result of a desktop automation action."""
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
