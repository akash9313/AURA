import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MissionRecord:
    mission_id: str = field(default_factory=lambda: f"m_{uuid.uuid4().hex[:8]}")
    goal: str = ""
    mission_type: str = "general"
    status: str = "completed"
    duration_ms: float = 0.0
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    capabilities_used: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    recoveries: List[str] = field(default_factory=list)
    reflection_summary: str = ""
    archived: bool = False
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "goal": self.goal,
            "mission_type": self.mission_type,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "capabilities_used": self.capabilities_used,
            "failures": self.failures,
            "recoveries": self.recoveries,
            "reflection_summary": self.reflection_summary,
            "archived": self.archived,
            "created_at": self.created_at,
        }


@dataclass
class MissionExperience:
    experience_id: str = field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:8]}")
    mission_type: str = "general"
    goal: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    success: bool = True
    confidence: float = 0.9
    capabilities_used: List[str] = field(default_factory=list)
    failure_reasons: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    embedding: List[float] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experience_id": self.experience_id,
            "mission_type": self.mission_type,
            "goal": self.goal,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "confidence": self.confidence,
            "capabilities_used": self.capabilities_used,
            "failure_reasons": self.failure_reasons,
            "lessons_learned": self.lessons_learned,
            "tags": self.tags,
            "created_at": self.created_at,
        }


@dataclass
class MissionCheckpointRecord:
    checkpoint_id: str = field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    mission_id: str = ""
    completed_tasks: List[str] = field(default_factory=list)
    task_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "mission_id": self.mission_id,
            "completed_tasks": self.completed_tasks,
            "task_outputs": self.task_outputs,
            "created_at": self.created_at,
        }
