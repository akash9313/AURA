import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class WorkflowTaskState(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowExecutionState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTaskExecution:
    task_id: str
    name: str
    capability: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowTaskState = WorkflowTaskState.PENDING
    retries_attempted: int = 0
    duration_ms: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "name": self.name,
            "capability": self.capability,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "status": self.status.value,
            "retries_attempted": self.retries_attempted,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
        }


@dataclass
class WorkflowProgress:
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    remaining_tasks: List[str] = field(default_factory=list)
    estimated_remaining_time: float = 0.0
    success_rate: float = 1.0
    current_capability: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks,
            "remaining_tasks": self.remaining_tasks,
            "estimated_remaining_time": self.estimated_remaining_time,
            "success_rate": self.success_rate,
            "current_capability": self.current_capability,
        }


@dataclass
class WorkflowExecutionResult:
    workflow_id: str
    success: bool
    state: WorkflowExecutionState
    completed_task_ids: List[str]
    failed_task_ids: List[str]
    duration_ms: float
    message: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "success": self.success,
            "state": self.state.value,
            "completed_task_ids": self.completed_task_ids,
            "failed_task_ids": self.failed_task_ids,
            "duration_ms": self.duration_ms,
            "message": self.message,
            "data": self.data,
        }
