from enum import Enum


class STTEvent(Enum):
    """Event definitions for Streaming STT."""
    PARTIAL_TRANSCRIPT = "partial_transcript"
    FINAL_TRANSCRIPT = "final_transcript"
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_FINISHED = "transcription_finished"
    TRANSCRIPTION_ERROR = "transcription_error"
