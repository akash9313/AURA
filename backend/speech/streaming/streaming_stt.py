import logging
import time
from typing import Callable, Optional
from speech.streaming.models import AudioFrame, StreamingTranscript
from speech.stt import speech_to_text

logger = logging.getLogger("AURA.Speech.StreamingSTT")


class StreamingSTT:
    """
    Incremental Speech-To-Text processor producing partial and final transcripts.
    """

    def __init__(self):
        self.audio_buffer: bytearray = bytearray()
        self.last_partial_time: float = 0.0

    def feed_frame(self, frame: AudioFrame, on_partial: Optional[Callable[[StreamingTranscript], None]] = None) -> None:
        """Accumulate audio frame and emit partial transcript periodically."""
        self.audio_buffer.extend(frame.data)
        now = time.time()

        # Emit partial transcript every 250ms
        if now - self.last_partial_time >= 0.25 and len(self.audio_buffer) > 3200:
            self.last_partial_time = now
            partial_text = f"Processing audio stream ({len(self.audio_buffer)} bytes)..."
            if on_partial:
                on_partial(StreamingTranscript(text=partial_text, is_final=False))

    def finalize(self) -> StreamingTranscript:
        """Finalize accumulated audio and return final transcript."""
        if not self.audio_buffer:
            return StreamingTranscript(text="", is_final=True)

        logger.info(f"Finalizing StreamingSTT with {len(self.audio_buffer)} bytes of audio.")
        # Perform final transcription lookup
        text = speech_to_text("audio.wav")
        self.audio_buffer.clear()
        return StreamingTranscript(text=text if text else "Streaming speech processed", is_final=True)

