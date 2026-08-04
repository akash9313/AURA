from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


class ConversationState(Enum):
    """Full Duplex Conversation State Machine Enum."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class InterruptionPayload:
    session_id: str
    interrupted_state: ConversationState
    interruption_latency_ms: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "interrupted_state": self.interrupted_state.value,
            "interruption_latency_ms": round(self.interruption_latency_ms, 2),
            "timestamp": self.timestamp,
        }


@dataclass
class ConversationSession:
    session_id: str
    current_state: ConversationState = ConversationState.IDLE
    start_time: float = field(default_factory=time.time)
    interruption_count: int = 0
    last_turn_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "start_time": self.start_time,
            "interruption_count": self.interruption_count,
            "last_turn_timestamp": self.last_turn_timestamp,
        }
