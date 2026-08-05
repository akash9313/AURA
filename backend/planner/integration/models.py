"""
Planner Integration Engine Domain Models.
Defines Mission, MissionRequest, MissionPriority, MissionExecutionMode, and MissionStatus.
Converts user requests into structured Missions for Planner and Workflow Engine execution.
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MissionPriority(Enum):
    """Priority level of a Mission."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MissionExecutionMode(Enum):
    """Execution mode of a Mission."""
    AUTOMATIC = "automatic"
    INTERACTIVE = "interactive"
    DRY_RUN = "dry_run"
    CONFIRM_REQUIRED = "confirm_required"


class MissionStatus(Enum):
    """Lifecycle status of a Mission."""
    CREATED = "created"
    PLANNED = "planned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class MissionRequest:
    """Raw user transcript converted into a structured Mission Request."""
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    original_user_request: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    priority: MissionPriority = MissionPriority.NORMAL
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "original_user_request": self.original_user_request,
            "context": self.context,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
        }


@dataclass
class Mission:
    """
    Master Mission Model.
    Represents a user request converted into a goal with required capabilities, planner confidence,
    and associated execution plan.
    """
    mission_id: str = field(default_factory=lambda: f"msn_{uuid.uuid4().hex[:8]}")
    original_user_request: str = ""
    goal: str = ""
    priority: MissionPriority = MissionPriority.NORMAL
    required_capabilities: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    planner_confidence: float = 1.0
    execution_mode: MissionExecutionMode = MissionExecutionMode.AUTOMATIC
    status: MissionStatus = MissionStatus.CREATED
    plan: Optional[Any] = None
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "original_user_request": self.original_user_request,
            "goal": self.goal,
            "priority": self.priority.value,
            "required_capabilities": self.required_capabilities,
            "expected_outcome": self.expected_outcome,
            "planner_confidence": self.planner_confidence,
            "execution_mode": self.execution_mode.value,
            "status": self.status.value,
            "plan": self.plan.to_dict() if hasattr(self.plan, "to_dict") else str(self.plan),
            "result_data": self.result_data,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
