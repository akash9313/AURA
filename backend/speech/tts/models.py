from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


class TTSState(Enum):
    IDLE = "idle"
    BUFFERING = "buffering"
    SYNTHESIZING = "synthesizing"
    PLAYING = "playing"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class AudioSegmentPayload:
    segment_id: str
    text: str
    audio_data: bytes
    duration_seconds: float
    synthesis_latency_ms: float
    voice_name: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "text": self.text,
            "duration_seconds": round(self.duration_seconds, 2),
            "synthesis_latency_ms": round(self.synthesis_latency_ms, 2),
            "voice_name": self.voice_name,
            "timestamp": self.timestamp,
        }


@dataclass
class PlaybackStatus:
    is_playing: bool
    current_segment_id: Optional[str] = None
    queue_length: int = 0
    cancelled_count: int = 0
