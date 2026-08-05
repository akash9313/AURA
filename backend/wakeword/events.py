"""
Wake Word Event Definitions.
Published to EventBus during wake word detection lifecycle.
"""

from enum import Enum


class WakeWordEvent(Enum):
    """Event definitions for Wake Word Engine."""
    WAKEWORD_LISTENING = "wakeword_listening"
    WAKEWORD_DETECTED = "wakeword_detected"
    WAKEWORD_TIMEOUT = "wakeword_timeout"
    WAKEWORD_ERROR = "wakeword_error"
