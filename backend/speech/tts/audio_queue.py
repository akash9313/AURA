import logging
import queue
import threading
from typing import Optional
from speech.tts.models import AudioSegmentPayload

logger = logging.getLogger("AURA.Speech.TTS.AudioQueue")


class AudioPlaybackQueue:
    """
    Thread-safe Audio Playback Queue supporting push, pop, pause, resume, and instant flush.
    Interruption-ready for stopping audio playback instantly when user interrupts.
    """

    def __init__(self, max_size: int = 50):
        self._queue: queue.Queue[AudioSegmentPayload] = queue.Queue(maxsize=max_size)
        self.is_paused: bool = False
        self.cancelled_count: int = 0
        self._lock = threading.Lock()

    def push(self, segment: AudioSegmentPayload) -> bool:
        try:
            self._queue.put_nowait(segment)
            logger.debug(f"Pushed audio segment '{segment.segment_id}' to playback queue (Length: {self.get_size()})")
            return True
        except queue.Full:
            logger.warning("AudioPlaybackQueue full: dropping segment.")
            return False

    def pop(self, timeout: float = 0.1) -> Optional[AudioSegmentPayload]:
        if self.is_paused:
            return None
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def flush(self) -> int:
        """Instantly flush all queued audio segments (interruption handling)."""
        flushed_count = 0
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    flushed_count += 1
                except queue.Empty:
                    break
            self.cancelled_count += flushed_count
        logger.info(f"Flushed {flushed_count} audio segments from playback queue.")
        return flushed_count

    def pause(self) -> None:
        self.is_paused = True
        logger.info("AudioPlaybackQueue paused.")

    def resume(self) -> None:
        self.is_paused = False
        logger.info("AudioPlaybackQueue resumed.")

    def get_size(self) -> int:
        return self._queue.qsize()

