"""
Mission Memory Integration Domain Models.
Defines OperationalMissionRecord and MissionSearchResult.
Stores operational experience independent from conversation memory.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OperationalMissionRecord:
    """
    Structured operational knowledge node representing a completed or failed mission.
    Contains task graph, timeline, capability usage, empirical verification evidence,
    recovery attempts, reflection insights, and lessons learned.
    """
    mission_id: str = field(default_factory=lambda: f"msn_mem_{uuid.uuid4().hex[:8]}")
    user_request: str = ""
    goal: str = ""
    mission_type: str = "workflow"
    status: str = "completed"
    task_graph: Dict[str, Any] = field(default_factory=dict)
    execution_timeline: List[Dict[str, Any]] = field(default_factory=list)
    capability_usage: List[str] = field(default_factory=list)
    verification_evidence: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    reflection_report: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "user_request": self.user_request,
            "goal": self.goal,
            "mission_type": self.mission_type,
            "status": self.status,
            "task_graph": self.task_graph,
            "execution_timeline": self.execution_timeline,
            "capability_usage": self.capability_usage,
            "verification_evidence": self.verification_evidence,
            "recovery_attempts": self.recovery_attempts,
            "reflection_report": self.reflection_report,
            "lessons_learned": self.lessons_learned,
            "performance_metrics": self.performance_metrics,
            "tags": self.tags,
            "created_at": self.created_at,
        }


@dataclass
class MissionSearchResult:
    """Result of semantic or metadata search over operational mission memory."""
    mission_record: OperationalMissionRecord
    similarity_score: float = 1.0
    matched_capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_record.mission_id,
            "goal": self.mission_record.goal,
            "similarity_score": round(self.similarity_score, 3),
            "matched_capabilities": self.matched_capabilities,
            "lessons_learned": self.mission_record.lessons_learned,
            "record": self.mission_record.to_dict(),
        }
