from enum import Enum


class TTSEvent(Enum):
    """Event definitions for Streaming Speech Synthesis."""
    TTS_STARTED = "tts_started"
    TTS_SEGMENT_READY = "tts_segment_ready"
    AUDIO_PLAY_STARTED = "audio_play_started"
    AUDIO_PLAY_FINISHED = "audio_play_finished"
    TTS_CANCELLED = "tts_cancelled"
    TTS_ERROR = "tts_error"
