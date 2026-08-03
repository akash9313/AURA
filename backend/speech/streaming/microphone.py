import asyncio
import logging
import time
from typing import Optional
from speech.streaming.models import AudioFrame

logger = logging.getLogger("AURA.Speech.Microphone")


class StreamingMicrophone:
    """
    Non-blocking microphone audio reader buffering PCM frames for VAD and STT.
    """

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.frame_size = int(self.sample_rate * (self.frame_duration_ms / 1000.0) * 2)  # 16-bit mono
        self.is_recording = False
        self.queue: asyncio.Queue[AudioFrame] = asyncio.Queue()

    async def start_recording(self) -> None:
        """Start non-blocking mic capture loop."""
        self.is_recording = True
        logger.info("StreamingMicrophone capture started.")

    async def stop_recording(self) -> None:
        """Stop mic capture loop."""
        self.is_recording = False
        logger.info("StreamingMicrophone capture stopped.")

    async def read_frame(self) -> Optional[AudioFrame]:
        """Read next 20ms audio frame from queue."""
        if not self.is_recording and self.queue.empty():
            return None
        try:
            return await asyncio.wait_for(self.queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            return None

    def push_raw_pcm(self, pcm_bytes: bytes) -> None:
        """Push raw PCM bytes into streaming queue (used by hardware callbacks)."""
        frame = AudioFrame(data=pcm_bytes, sample_rate=self.sample_rate)
        try:
            self.queue.put_nowait(frame)
        except Exception as e:
            logger.warning(f"Microphone queue overflow: {e}")
