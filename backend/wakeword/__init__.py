"""
AURA Wake Word Engine Subsystem (`backend/wakeword/`).
Provides continuous always-listening wake word detection with provider abstraction.
"""

from wakeword.audio_buffer import AudioRingBuffer
from wakeword.configuration import WakeWordConfig
from wakeword.events import WakeWordEvent
from wakeword.models import WakeWordDetectionResult, WakeWordEngineState
from wakeword.openwakeword_provider import OpenWakeWordProvider
from wakeword.provider import BaseWakeWordProvider
from wakeword.service import WakeWordService

__all__ = [
    "WakeWordService",
    "BaseWakeWordProvider",
    "OpenWakeWordProvider",
    "AudioRingBuffer",
    "WakeWordConfig",
    "WakeWordDetectionResult",
    "WakeWordEngineState",
    "WakeWordEvent",
]
