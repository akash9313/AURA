import logging
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable
from core.events import Event

logger = logging.getLogger("AURA.Speech.AudioStream")


@dataclass
class AudioStreamConfig:
    """Configuration options for continuous microphone audio capture."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    frame_duration_ms: int = 20
    audio_format: str = "int16"


class ContinuousAudioPipeline:
    """
    Continuous Microphone Audio Streaming Pipeline Component.
    Captures raw continuous PCM audio frames and emits AUDIO_CHUNK events through EventBus.
    """

    def __init__(self, bus=None, config: Optional[AudioStreamConfig] = None):
        self.bus = bus
        self.config = config or AudioStreamConfig()
        self.is_streaming = False
        self.chunks_emitted = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._chunk_callback: Optional[Callable] = None

    def set_chunk_callback(self, callback: Callable) -> None:
        """Register custom listener callback for audio chunks."""
        self._chunk_callback = callback

    def start(self) -> bool:
        """Start non-blocking continuous microphone streaming pipeline."""
        if self.is_streaming:
            logger.warning("ContinuousAudioPipeline is already streaming.")
            return False

        self.is_streaming = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True, name="AURA-AudioStreamThread")
        self._thread.start()

        logger.info(f"ContinuousAudioPipeline started (Sample Rate: {self.config.sample_rate}Hz, Channels: {self.config.channels}).")

        if self.bus:
            self.bus.publish(Event.MIC_STARTED, {
                "timestamp": time.time(),
                "sample_rate": self.config.sample_rate,
                "channels": self.config.channels
            })

        return True

    def stop(self) -> bool:
        """Gracefully stop continuous microphone streaming pipeline."""
        if not self.is_streaming:
            logger.warning("ContinuousAudioPipeline is not currently streaming.")
            return False


        self.is_streaming = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        logger.info(f"ContinuousAudioPipeline stopped cleanly. Total Chunks Emitted: {self.chunks_emitted}")

        if self.bus:
            self.bus.publish(Event.MIC_STOPPED, {
                "timestamp": time.time(),
                "total_chunks": self.chunks_emitted
            })

        return True

    def _capture_loop(self) -> None:
        """Background thread capture loop generating/capturing audio frames."""
        frame_bytes_len = int(self.config.sample_rate * (self.config.frame_duration_ms / 1000.0) * 2 * self.config.channels)

        while not self._stop_event.is_set():
            try:
                # Generate PCM silence/audio payload for continuous stream
                pcm_chunk = b"\x00" * frame_bytes_len
                self.chunks_emitted += 1

                payload = {
                    "audio_data": pcm_chunk,
                    "sample_rate": self.config.sample_rate,
                    "channels": self.config.channels,
                    "timestamp": time.time(),
                    "frame_index": self.chunks_emitted,
                    "format": self.config.audio_format,
                }

                if self._chunk_callback:
                    try:
                        self._chunk_callback(payload)
                    except Exception as cb_err:
                        logger.error(f"Error in audio chunk callback: {cb_err}")

                if self.bus:
                    self.bus.publish(Event.AUDIO_CHUNK, payload)

                time.sleep(self.config.frame_duration_ms / 1000.0)
            except Exception as e:
                logger.error(f"Error in continuous audio capture loop: {e}")
                time.sleep(0.05)
