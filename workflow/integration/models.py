import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MissionExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VERIFICATION_FAILED = "verification_failed"


@dataclass
class TaskExecutionProgress:
    task_id: str
    name: str
    status: str = "pending"
    duration_sec: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "duration_sec": round(self.duration_sec, 3),
            "error": self.error,
        }


@dataclass
class MissionExecutionResult:
    mission_id: str
    status: MissionExecutionStatus = MissionExecutionStatus.PENDING
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    execution_time_sec: float = 0.0
    verification_result: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    summary: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "status": self.status.value,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "execution_time_sec": round(self.execution_time_sec, 3),
            "verification_result": self.verification_result,
            "recovery_attempts": self.recovery_attempts,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }
