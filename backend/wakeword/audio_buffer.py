"""
Thread-safe Circular Audio Ring Buffer.
Buffers microphone PCM audio chunks for streaming wake word feature extraction.
"""

import collections
import threading
from typing import Optional


class AudioRingBuffer:
    """
    Circular ring buffer for PCM audio bytes.
    """

    def __init__(self, capacity_bytes: int = 16000 * 2 * 5): # 5 seconds of 16kHz 16-bit audio
        self.capacity = capacity_bytes
        self._buffer = collections.deque()
        self._size = 0
        self._lock = threading.Lock()

    def write(self, data: bytes) -> None:
        """Append audio bytes to buffer, dropping oldest data when over capacity."""
        if not data:
            return
        with self._lock:
            self._buffer.append(data)
            self._size += len(data)

            while self._size > self.capacity and self._buffer:
                popped = self._buffer.popleft()
                self._size -= len(popped)

    def read_all(self) -> bytes:
        """Read and clear all accumulated audio bytes."""
        with self._lock:
            data = b"".join(self._buffer)
            self._buffer.clear()
            self._size = 0
            return data

    def clear(self) -> None:
        """Clear buffer."""
        with self._lock:
            self._buffer.clear()
            self._size = 0
