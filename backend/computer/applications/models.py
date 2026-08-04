"""
Application Manager Domain Models.
Defines platform-independent AURAApplication objects, ApplicationState enum, launch options, and action results.
Hides raw OS process objects behind clean AURA Application domain models.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ApplicationState(Enum):
    """Lifecycle state of a desktop application."""
    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    CLOSING = "closing"
    CLOSED = "closed"
    CRASHED = "crashed"


@dataclass
class AURAApplication:
    """Platform-independent AURA Application representation."""
    app_id: str = field(default_factory=lambda: f"app_{uuid.uuid4().hex[:8]}")
    name: str = ""
    executable_path: str = ""
    process_id: int = 0
    status: ApplicationState = ApplicationState.STARTING
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    window_ids: List[str] = field(default_factory=list)
    launch_time: float = field(default_factory=time.time)
    working_directory: str = ""
    command_line: List[str] = field(default_factory=list)
    is_ready: bool = False
    _internal_process_ref: Optional[Any] = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "executable_path": self.executable_path,
            "process_id": self.process_id,
            "status": self.status.value,
            "cpu_percent": self.cpu_percent,
            "memory_mb": self.memory_mb,
            "window_count": len(self.window_ids),
            "launch_time": self.launch_time,
            "working_directory": self.working_directory,
            "command_line": self.command_line,
            "is_ready": self.is_ready,
        }


@dataclass
class ApplicationLaunchOptions:
    """Options for launching a desktop application."""
    executable_or_name: str
    args: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    wait_ready: bool = True
    timeout_ms: float = 10000.0


@dataclass
class ApplicationResult:
    """Unified execution result of an application operation."""
    success: bool
    app_id: str
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "app_id": self.app_id,
            "action": self.action,
            "message": self.message,
            "data": self.data or {},
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp,
        }
