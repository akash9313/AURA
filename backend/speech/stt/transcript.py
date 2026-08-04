import logging
from typing import Optional
from speech.stt.models import FinalTranscript, PartialTranscript

logger = logging.getLogger("AURA.Speech.STT.Transcript")


class TranscriptFormatter:
    """Formatter and sanitizer for Partial and Final transcripts."""

    def format_partial(self, raw_text: str, duration: float, confidence: float = 0.90) -> PartialTranscript:
        clean_text = raw_text.strip()
        return PartialTranscript(
            text=clean_text,
            confidence=confidence,
            duration_seconds=duration
        )

    def format_final(self, raw_text: str, duration: float, inference_time_ms: float, confidence: float = 0.95) -> FinalTranscript:
        clean_text = raw_text.strip()
        return FinalTranscript(
            text=clean_text,
            confidence=confidence,
            duration_seconds=duration,
            inference_time_ms=inference_time_ms
        )
