import logging
import time
from typing import Optional
from speech.stt.configuration import STTConfig

logger = logging.getLogger("AURA.Speech.STT.Segmenter")


class UtteranceSegmenter:
    """
    Logical Utterance Segmenter.
    Determines boundary conditions for splitting continuous speech into discrete utterances.
    """

    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or STTConfig()
        self.utterance_start_time: Optional[float] = None

    def start_utterance(self) -> None:
        self.utterance_start_time = time.time()

    def should_finalize(self, is_vad_ended: bool = False, silence_duration_seconds: float = 0.0) -> bool:
        if is_vad_ended:
            return True

        if self.utterance_start_time:
            elapsed = time.time() - self.utterance_start_time
            if elapsed >= self.config.max_utterance_duration_seconds:
                logger.info(f"Finalizing utterance due to max duration limit ({elapsed:.1f}s >= {self.config.max_utterance_duration_seconds}s)")
                return True

        if silence_duration_seconds >= 1.5:
            return True

        return False

    def reset(self) -> None:
        self.utterance_start_time = None
