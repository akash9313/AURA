from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PermissionLevel(Enum):
    """Safety permission classification levels."""
    ALWAYS_ALLOWED = "always_allowed"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"
    ADMIN_REQUIRED = "admin_required"


class ActionType(Enum):
    """Categories of Windows automation operations."""
    LAUNCH_APP = "launch_app"
    CLOSE_APP = "close_app"
    FOCUS_WINDOW = "focus_window"
    TYPE_TEXT = "type_text"
    HOTKEY = "hotkey"
    CLICK = "click"
    DRAG = "drag"
    CLIPBOARD_READ = "clipboard_read"
    CLIPBOARD_WRITE = "clipboard_write"
    SCREENSHOT = "screenshot"


@dataclass
class WindowInfo:
    """Metadata representing an open OS window."""
    title: str
    handle: int = 0
    process_name: str = ""
    pid: int = 0
    bounds: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "width": 800, "height": 600})
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "handle": self.handle,
            "process_name": self.process_name,
            "pid": self.pid,
            "bounds": self.bounds,
            "is_active": self.is_active
        }


@dataclass
class ScreenResolution:
    """Screen display dimensions."""
    width: int
    height: int
    dpi_scale: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "dpi_scale": self.dpi_scale
        }


@dataclass
class AutomationResult:
    """Standardized result returned by all Windows automation operations."""
    success: bool
    message: str
    data: Optional[Any] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "execution_time": self.execution_time
        }


@dataclass
class ActionLog:
    """Structured log record for executed OS actions."""
    action_type: ActionType
    parameters: Dict[str, Any]
    duration: float
    success: bool
    failure_reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type.value,
            "parameters": self.parameters,
            "duration": self.duration,
            "success": self.success,
            "failure_reason": self.failure_reason
        }
