from enum import Enum


class VADEvent(Enum):
    """Event definitions for Voice Activity Detection."""
    VOICE_STARTED = "voice_started"
    VOICE_CONTINUING = "voice_continuing"
    VOICE_ENDED = "voice_ended"
    SILENCE_DETECTED = "silence_detected"
