"""
Conversation Engine Domain Models.
Defines ConversationState, ConversationSession, and InterruptionPayload.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ConversationState(Enum):
    """Voice Conversation State Machine Enum."""
    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    RESPONDING = "responding"
    SPEAKING = "speaking"  # Alias for RESPONDING
    WAITING_FOR_FOLLOWUP = "waiting_for_followup"
    INTERRUPTED = "interrupted"
    ERROR = "error"


@dataclass
class InterruptionPayload:
    """Telemetry payload recorded when user interrupts active TTS response."""
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
    """Active voice conversation session tracking."""
    session_id: str
    current_state: ConversationState = ConversationState.IDLE
    start_time: float = field(default_factory=time.time)
    interruption_count: int = 0
    last_turn_timestamp: float = field(default_factory=time.time)
    turn_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "start_time": self.start_time,
            "interruption_count": self.interruption_count,
            "last_turn_timestamp": self.last_turn_timestamp,
            "turn_count": self.turn_count,
        }
