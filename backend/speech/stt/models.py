from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


class STTState(Enum):
    IDLE = "idle"
    BUFFERING = "buffering"
    TRANSCRIBING = "transcribing"
    FINALIZING = "finalizing"
    ERROR = "error"


@dataclass
class PartialTranscript:
    text: str
    confidence: float = 0.90
    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "is_final": False,
        }


@dataclass
class FinalTranscript:
    text: str
    confidence: float = 0.95
    timestamp: float = field(default_factory=time.time)
    duration_seconds: float = 0.0
    inference_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "inference_time_ms": self.inference_time_ms,
            "is_final": True,
        }
