"""
Browser Capability Validation Domain Models.
Defines CapabilityValidationStatus, CapabilityValidationResult, MissionValidationResult, and ValidationMetrics.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CapabilityValidationStatus(Enum):
    """Status of browser capability validation."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    RECOVERED = "recovered"


@dataclass
class CapabilityValidationResult:
    """Result of validating an individual browser capability."""
    capability_name: str
    status: CapabilityValidationStatus = CapabilityValidationStatus.PENDING
    duration_sec: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_name": self.capability_name,
            "status": self.status.value,
            "duration_sec": round(self.duration_sec, 3),
            "evidence": self.evidence,
            "recovery_attempts": self.recovery_attempts,
            "error": self.error,
        }


@dataclass
class MissionValidationResult:
    """Validation result for an end-to-end Test Mission."""
    mission_id: str
    mission_name: str
    status: CapabilityValidationStatus = CapabilityValidationStatus.PENDING
    capability_results: List[CapabilityValidationResult] = field(default_factory=list)
    total_duration_sec: float = 0.0
    verification_evidence: Dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    success_rate: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "mission_name": self.mission_name,
            "status": self.status.value,
            "capability_results": [c.to_dict() for c in self.capability_results],
            "total_duration_sec": round(self.total_duration_sec, 3),
            "verification_evidence": self.verification_evidence,
            "recovery_attempts": self.recovery_attempts,
            "success_rate": round(self.success_rate, 2),
            "timestamp": self.timestamp,
        }


@dataclass
class ValidationMetrics:
    """Aggregated validation report metrics across all test missions."""
    total_missions: int = 0
    passed_missions: int = 0
    failed_missions: int = 0
    overall_success_rate: float = 0.0
    total_duration_sec: float = 0.0
    avg_mission_duration_sec: float = 0.0
    total_recovery_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_missions": self.total_missions,
            "passed_missions": self.passed_missions,
            "failed_missions": self.failed_missions,
            "overall_success_rate": round(self.overall_success_rate, 2),
            "total_duration_sec": round(self.total_duration_sec, 3),
            "avg_mission_duration_sec": round(self.avg_mission_duration_sec, 3),
            "total_recovery_attempts": self.total_recovery_attempts,
        }
