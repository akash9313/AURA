import logging
import threading
import time
from typing import Optional, Callable
from speech.tts.audio_queue import AudioPlaybackQueue
from speech.tts.models import AudioSegmentPayload, PlaybackStatus

logger = logging.getLogger("AURA.Speech.TTS.AudioPlayer")


class AudioPlayerEngine:
    """
    Non-blocking Audio Player Engine for Streaming Speech Synthesis segments.
    Consumes AudioSegmentPayload objects from AudioPlaybackQueue and streams audio output.
    """

    def __init__(self, queue: AudioPlaybackQueue):
        self.queue = queue
        self.is_playing: bool = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._on_segment_start: Optional[Callable] = None
        self._on_segment_finish: Optional[Callable] = None

    def set_callbacks(self, on_start: Callable, on_finish: Callable) -> None:
        self._on_segment_start = on_start
        self._on_segment_finish = on_finish

    def start(self) -> None:
        if self.is_playing:
            return
        self.is_playing = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._playback_loop, daemon=True, name="AURA-AudioPlayerThread")
        self._thread.start()
        logger.info("AudioPlayerEngine started.")

    def stop(self) -> None:
        self.is_playing = False
        self._stop_event.set()
        self.queue.flush()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        logger.info("AudioPlayerEngine stopped.")

    def _playback_loop(self) -> None:

        while not self._stop_event.is_set():
            segment = self.queue.pop(timeout=0.05)
            if segment and not self._stop_event.is_set():
                logger.info(f"Playing audio segment '{segment.segment_id}' ('{segment.text[:30]}...')")
                if self._on_segment_start:
                    self._on_segment_start(segment)

                # Simulate audio playback duration
                play_dur = max(0.05, min(segment.duration_seconds, 0.2))
                time.sleep(play_dur)

                if self._on_segment_finish and not self._stop_event.is_set():
                    self._on_segment_finish(segment)
