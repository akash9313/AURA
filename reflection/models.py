import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RecommendationType(Enum):
    PREFER_CAPABILITY = "prefer_capability"
    INCREASE_TIMEOUT = "increase_timeout"
    REDUCE_RETRY_COUNT = "reduce_retry_count"
    PARALLELIZE_TASKS = "parallelize_tasks"
    USE_ALTERNATIVE_STRATEGY = "use_alternative_strategy"
    IMPROVE_VERIFICATION_RULE = "improve_verification_rule"


@dataclass
class Recommendation:
    recommendation_id: str = field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    type: RecommendationType = RecommendationType.PREFER_CAPABILITY
    description: str = ""
    confidence_score: float = 0.85
    supporting_evidence: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    expected_benefit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "type": self.type.value,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "supporting_evidence": self.supporting_evidence,
            "affected_components": self.affected_components,
            "expected_benefit": self.expected_benefit,
        }


@dataclass
class PatternInsight:
    pattern_id: str = field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:8]}")
    pattern_type: str = ""
    frequency: int = 1
    description: str = ""
    impact: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "frequency": self.frequency,
            "description": self.description,
            "impact": self.impact,
        }


@dataclass
class TaskMetric:
    task_id: str
    capability: str
    duration_ms: float
    retries: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "capability": self.capability,
            "duration_ms": self.duration_ms,
            "retries": self.retries,
            "status": self.status,
        }


@dataclass
class ReflectionReport:
    report_id: str = field(default_factory=lambda: f"rep_{uuid.uuid4().hex[:8]}")
    workflow_id: str = ""
    mission_summary: str = ""
    success_rate: float = 1.0
    total_duration_ms: float = 0.0
    task_statistics: List[TaskMetric] = field(default_factory=list)
    patterns_detected: List[PatternInsight] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "workflow_id": self.workflow_id,
            "mission_summary": self.mission_summary,
            "success_rate": self.success_rate,
            "total_duration_ms": self.total_duration_ms,
            "task_statistics": [t.to_dict() for t in self.task_statistics],
            "patterns_detected": [p.to_dict() for p in self.patterns_detected],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "created_at": self.created_at,
        }
