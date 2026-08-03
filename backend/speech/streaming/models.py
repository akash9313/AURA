from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time


class SpeechState(Enum):
    """Voice pipeline state machine stages."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"


@dataclass
class AudioFrame:
    """Represents a 20ms chunk of raw PCM audio data."""
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    timestamp: float = field(default_factory=time.time)

    def size(self) -> int:
        return len(self.data)


@dataclass
class VADSegment:
    """Voice Activity Detection evaluation result."""
    is_speech: bool
    energy_level: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class StreamingTranscript:
    """Incremental speech recognition result."""
    text: str
    is_final: bool = False
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "is_final": self.is_final,
            "confidence": self.confidence
        }


@dataclass
class LatencyMetrics:
    """Telemetry metrics tracking latency across voice pipeline stages."""
    mic_latency_ms: float = 0.0
    stt_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    tts_latency_ms: float = 0.0
    total_roundtrip_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mic_latency_ms": self.mic_latency_ms,
            "stt_latency_ms": self.stt_latency_ms,
            "llm_latency_ms": self.llm_latency_ms,
            "tts_latency_ms": self.tts_latency_ms,
            "total_roundtrip_ms": self.total_roundtrip_ms
        }
