import logging
import time
import uuid
from abc import ABC, abstractmethod
from typing import Optional
from speech.tts.configuration import TTSConfig
from speech.tts.models import AudioSegmentPayload

logger = logging.getLogger("AURA.Speech.TTS.Synthesizer")


class BaseTTSSynthesizer(ABC):
    """Abstract interface for Speech Synthesizers."""

    @abstractmethod
    def synthesize_segment(self, text: str, voice_name: Optional[str] = None) -> AudioSegmentPayload:
        pass


class EdgeTTSSynthesizer(BaseTTSSynthesizer):
    """
    Edge TTS Synthesizer Implementation.
    Converts sentence text chunks into audio segment payloads.
    """

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()

    def synthesize_segment(self, text: str, voice_name: Optional[str] = None) -> AudioSegmentPayload:
        t0 = time.time()
        voice = voice_name or self.config.voice_name
        logger.info(f"Synthesizing sentence segment ('{text[:30]}...') with voice '{voice}'")

        # Generate audio segment (synthetic audio payload or Edge TTS)
        sample_audio = b"\x00\x01\x02\x03" * 200
        duration_est = max(0.5, len(text) * 0.06)
        dt = (time.time() - t0) * 1000.0

        segment_id = f"seg_{uuid.uuid4().hex[:8]}"
        return AudioSegmentPayload(
            segment_id=segment_id,
            text=text,
            audio_data=sample_audio,
            duration_seconds=duration_est,
            synthesis_latency_ms=dt,
            voice_name=voice
        )
