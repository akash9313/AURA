from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import time


class WorkflowState(Enum):
    """Lifecycle state machine for workflows."""
    CREATED = "created"
    VALIDATING = "validating"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


class TaskState(Enum):
    """Lifecycle state machine for individual workflow tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class TaskType(Enum):
    """Categorized domain types for workflow tasks."""
    BROWSER = "browser"
    DESKTOP = "desktop"
    VISION = "vision"
    MEMORY = "memory"
    REASONING = "reasoning"
    FILE = "file"
    TERMINAL = "terminal"
    PLUGIN = "plugin"
    CUSTOM = "custom"


@dataclass
class TaskMetric:
    """Telemetry metrics for task execution."""
    start_time: float = 0.0
    end_time: float = 0.0
    execution_time_ms: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None


@dataclass
class WorkflowMetric:
    """Telemetry metrics for total workflow execution."""
    created_at: float = field(default_factory=time.time)
    started_at: float = 0.0
    completed_at: float = 0.0
    total_duration_ms: float = 0.0
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    retried_tasks: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_ms": self.total_duration_ms,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "retried_tasks": self.retried_tasks,
        }
