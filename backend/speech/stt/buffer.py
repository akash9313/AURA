import logging
import threading

logger = logging.getLogger("AURA.Speech.STT.Buffer")


class AudioBufferManager:
    """
    Efficient rolling PCM audio buffer for streaming Speech-to-Text inference.
    Guarantees low latency, minimal memory footprint, and thread-safe operations.
    """

    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024):
        self.max_size_bytes = max_size_bytes
        self._buffer = bytearray()
        self._lock = threading.Lock()
        self.dropped_chunks: int = 0

    def push_chunk(self, pcm_bytes: bytes) -> None:
        if not pcm_bytes:
            return

        with self._lock:
            if len(self._buffer) + len(pcm_bytes) > self.max_size_bytes:
                self.dropped_chunks += 1
                logger.warning("STT AudioBuffer overflow: dropping oldest PCM frame.")
                overflow_len = (len(self._buffer) + len(pcm_bytes)) - self.max_size_bytes
                del self._buffer[:overflow_len]

            self._buffer.extend(pcm_bytes)

    def get_pcm_bytes(self) -> bytes:
        with self._lock:
            return bytes(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()

    def get_size(self) -> int:
        with self._lock:
            return len(self._buffer)

