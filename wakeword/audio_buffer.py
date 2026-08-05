import collections
import threading
from typing import Optional


class AudioRingBuffer:
    def __init__(self, capacity_bytes: int = 16000 * 2 * 5):
        self.capacity = capacity_bytes
        self._buffer = collections.deque()
        self._size = 0
        self._lock = threading.Lock()

    def write(self, data: bytes) -> None:
        if not data:
            return
        with self._lock:
            self._buffer.append(data)
            self._size += len(data)

            while self._size > self.capacity and self._buffer:
                popped = self._buffer.popleft()
                self._size -= len(popped)

    def read_all(self) -> bytes:
        with self._lock:
            data = b"".join(self._buffer)
            self._buffer.clear()
            self._size = 0
            return data

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
            self._size = 0
