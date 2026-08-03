import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from cognition.models import CognitiveDecision, CognitiveStateSnapshot, ReflectionRecord

logger = logging.getLogger("AURA.Cognition.Context")


class CognitiveContext:
    """
    Maintains structured observability timelines for cognitive execution requests.
    """

    def __init__(self, request_id: str = ""):
        self.request_id = request_id
        self.reasoning_timeline: List[Dict[str, Any]] = []
        self.decision_timeline: List[Dict[str, Any]] = []
        self.tool_timeline: List[Dict[str, Any]] = []
        self.memory_access_timeline: List[Dict[str, Any]] = []
        self.reflection_summary: Optional[Dict[str, Any]] = None

    def log_reasoning(self, step: str, details: Dict[str, Any]) -> None:
        self.reasoning_timeline.append({
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "details": details
        })

    def log_decision(self, decision: CognitiveDecision) -> None:
        self.decision_timeline.append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision.to_dict()
        })

    def log_tool_execution(self, tool_name: str, status: str, duration: float) -> None:
        self.tool_timeline.append({
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "status": status,
            "duration": duration
        })

    def log_memory_access(self, memory_type: str, query: str) -> None:
        self.memory_access_timeline.append({
            "timestamp": datetime.now().isoformat(),
            "memory_type": memory_type,
            "query": query
        })

    def set_reflection(self, reflection: ReflectionRecord) -> None:
        self.reflection_summary = reflection.to_dict()

    def get_summary(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "reasoning_steps": len(self.reasoning_timeline),
            "decisions": self.decision_timeline,
            "tools_executed": self.tool_timeline,
            "memory_accesses": self.memory_access_timeline,
            "reflection": self.reflection_summary
        }
