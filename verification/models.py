import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EvidenceType(Enum):
    UI_AUTOMATION = "ui_automation"
    SCREEN_VISION = "screen_vision"
    OCR = "ocr"
    BROWSER_DOM = "browser_dom"
    FILE_SYSTEM = "file_system"
    APPLICATION_STATE = "application_state"
    WORKFLOW_EVENT = "workflow_event"


class FailureType(Enum):
    NONE = "none"
    ELEMENT_NOT_FOUND = "element_not_found"
    STATE_MISMATCH = "state_mismatch"
    TIMEOUT = "timeout"
    PERMISSION_DENIED = "permission_denied"
    LOW_CONFIDENCE = "low_confidence"
    UNEXPECTED_RESPONSE = "unexpected_response"


@dataclass
class Evidence:
    evidence_id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:8]}")
    evidence_type: EvidenceType = EvidenceType.WORKFLOW_EVENT
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "evidence_type": self.evidence_type.value,
            "source": self.source,
            "data": self.data,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


@dataclass
class GoalVerificationRequest:
    goal_id: str
    goal_description: str
    expected_outcome: Dict[str, Any]
    strategies: List[EvidenceType] = field(default_factory=list)
    min_confidence_threshold: float = 0.75


@dataclass
class GoalVerificationResult:
    verified: bool
    confidence_score: float
    evidence_list: List[Evidence]
    reason: str
    failure_type: FailureType = FailureType.NONE
    recovery_action: Optional[str] = None
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verified": self.verified,
            "confidence_score": self.confidence_score,
            "evidence_count": len(self.evidence_list),
            "evidence_list": [e.to_dict() for e in self.evidence_list],
            "reason": self.reason,
            "failure_type": self.failure_type.value,
            "recovery_action": self.recovery_action,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }
