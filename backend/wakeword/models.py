"""
Wake Word Engine Domain Models.
Defines WakeWordDetectionResult and WakeWordEngineState.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class WakeWordEngineState(Enum):
    """Status of the Wake Word Engine loop."""
    STOPPED = "stopped"
    LISTENING = "listening"
    DETECTED = "detected"
    ERROR = "error"


@dataclass
class WakeWordDetectionResult:
    """Result returned when a wake word feature frame is processed."""
    detected: bool = False
    wake_word: str = ""
    confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detected": self.detected,
            "wake_word": self.wake_word,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }
