from enum import Enum


class WakeWordEvent(Enum):
    WAKEWORD_LISTENING = "wakeword_listening"
    WAKEWORD_DETECTED = "wakeword_detected"
    WAKEWORD_TIMEOUT = "wakeword_timeout"
    WAKEWORD_ERROR = "wakeword_error"
