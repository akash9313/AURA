from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class GoalType(Enum):
    """Classification types for Cognitive Goals."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    DEPENDENT = "dependent"
    BACKGROUND = "background"


class GoalStatus(Enum):
    """Execution lifecycle status for Goals."""
    PENDING = "pending"
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class RiskLevel(Enum):
    """Risk rating levels for cognitive decision evaluation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConfidenceScore:
    """Rating container for decision confidence & risk analysis."""
    score: float  # 0.0 to 1.0
    reason: str
    risk_level: RiskLevel = RiskLevel.LOW
    recommended_action: str = "execute"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "reason": self.reason,
            "risk_level": self.risk_level.value,
            "recommended_action": self.recommended_action
        }


@dataclass
class CognitiveDecision:
    """Decision Engine evaluation result selecting execution strategy."""
    needs_direct_answer: bool = False
    needs_memory: bool = False
    needs_tools: bool = False
    needs_browser: bool = False
    needs_vision: bool = False
    needs_user_confirmation: bool = False
    selected_tools: List[str] = field(default_factory=list)
    reasoning_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "needs_direct_answer": self.needs_direct_answer,
            "needs_memory": self.needs_memory,
            "needs_tools": self.needs_tools,
            "needs_browser": self.needs_browser,
            "needs_vision": self.needs_vision,
            "needs_user_confirmation": self.needs_user_confirmation,
            "selected_tools": self.selected_tools,
            "reasoning_summary": self.reasoning_summary
        }


@dataclass
class ReflectionRecord:
    """Post-execution assessment and memory learning insights."""
    was_successful: bool
    execution_time: float = 0.0
    failed_tools: List[str] = field(default_factory=list)
    plan_improvements: List[str] = field(default_factory=list)
    should_update_memory: bool = False
    memory_insights: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "was_successful": self.was_successful,
            "execution_time": self.execution_time,
            "failed_tools": self.failed_tools,
            "plan_improvements": self.plan_improvements,
            "should_update_memory": self.should_update_memory,
            "memory_insights": self.memory_insights,
            "summary": self.summary
        }


@dataclass
class CognitiveStateSnapshot:
    """Snapshot representation of active cognitive runtime state."""
    user_id: str = "default_user"
    goal_id: str = ""
    workflow_id: str = ""
    active_tool: str = ""
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "goal_id": self.goal_id,
            "workflow_id": self.workflow_id,
            "active_tool": self.active_tool,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }
