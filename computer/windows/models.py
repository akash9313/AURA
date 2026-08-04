import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class WindowState(Enum):
    NORMAL = "normal"
    FOCUSED = "focused"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    HIDDEN = "hidden"
    CLOSED = "closed"


@dataclass
class AURAWindow:
    window_id: str = field(default_factory=lambda: f"win_{uuid.uuid4().hex[:8]}")
    app_id: str = "desktop_app"
    title: str = ""
    bounds: Tuple[int, int, int, int] = (0, 0, 800, 600)
    state: WindowState = WindowState.NORMAL
    is_visible: bool = True
    process_id: int = 0
    class_name: str = ""
    creation_time: float = field(default_factory=time.time)
    last_active_time: float = field(default_factory=time.time)
    children: List[str] = field(default_factory=list)
    _internal_handle: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "window_id": self.window_id,
            "app_id": self.app_id,
            "title": self.title,
            "bounds": self.bounds,
            "state": self.state.value,
            "is_visible": self.is_visible,
            "process_id": self.process_id,
            "class_name": self.class_name,
            "creation_time": self.creation_time,
            "last_active_time": self.last_active_time,
            "child_count": len(self.children),
        }


@dataclass
class WindowSearchQuery:
    title: Optional[str] = None
    app_name: Optional[str] = None
    process_id: Optional[int] = None
    regex_pattern: Optional[str] = None
    class_name: Optional[str] = None
    partial_match: bool = True


@dataclass
class WindowActionResult:
    success: bool
    window_id: str
    action: str
    message: str
    state: Optional[WindowState] = None
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "window_id": self.window_id,
            "action": self.action,
            "message": self.message,
            "state": self.state.value if self.state else None,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }
