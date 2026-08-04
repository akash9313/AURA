from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class VADState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    SILENCE = "silence"


@dataclass
class AudioEnergyProfile:
    """Calculated audio energy and noise profile for a frame."""
    rms_energy: float
    is_above_threshold: bool
    background_noise_floor: float
    confidence: float = 0.95


@dataclass
class VADSegment:
    """VAD processing segment result."""
    state: VADState
    is_speech: bool
    energy: float
    confidence: float
    duration_seconds: float = 0.0
    timestamp: float = field(default_factory=time.time)
