import collections
import logging

logger = logging.getLogger("AURA.Speech.Buffer")


class CircularAudioBuffer:
    """
    Circular sliding audio frame buffer for pre-roll VAD detection.
    """

    def __init__(self, max_frames: int = 50):
        self.buffer = collections.deque(maxlen=max_frames)

    def append(self, frame_bytes: bytes) -> None:
        self.buffer.append(frame_bytes)

    def get_all(self) -> bytes:
        return b"".join(self.buffer)

    def clear(self) -> None:
        self.buffer.clear()

