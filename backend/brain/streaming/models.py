from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class StreamState(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    STREAMING = "streaming"
    FINISHED = "finished"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class TokenChunk:
    token: str
    token_index: int
    timestamp: float = field(default_factory=time.time)
    is_first_token: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "token_index": self.token_index,
            "timestamp": self.timestamp,
            "is_first_token": self.is_first_token,
        }


@dataclass
class StreamingResponsePayload:
    full_text: str
    total_tokens: int
    first_token_latency_ms: float
    total_duration_ms: float
    finish_reason: str = "completed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "full_text": self.full_text,
            "total_tokens": self.total_tokens,
            "first_token_latency_ms": round(self.first_token_latency_ms, 2),
            "total_duration_ms": round(self.total_duration_ms, 2),
            "finish_reason": self.finish_reason,
        }
