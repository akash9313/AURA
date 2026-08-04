import logging
from typing import List, Optional
from speech.tts.configuration import TTSConfig

logger = logging.getLogger("AURA.Speech.TTS.SentenceBuffer")


class SentenceBuffer:
    """
    Sentence Boundary Buffer.
    Accumulates token stream chunks and detects logical sentence boundaries for incremental TTS synthesis.
    """

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._accumulator: str = ""

    def push_token(self, token: str) -> Optional[str]:
        """
        Append token chunk and return complete sentence if boundary detected.
        """
        self._accumulator += token

        # Check for sentence delimiters
        for delimiter in self.config.sentence_delimiters:
            if delimiter in self._accumulator:
                idx = self._accumulator.find(delimiter) + len(delimiter)
                sentence = self._accumulator[:idx].strip()
                self._accumulator = self._accumulator[idx:]
                if sentence:
                    logger.debug(f"Sentence boundary detected: '{sentence}'")
                    return sentence

        # Force flush if buffer exceeds maximum length
        if len(self._accumulator) >= self.config.max_sentence_length_chars:
            sentence = self._accumulator.strip()
            self._accumulator = ""
            if sentence:
                logger.info(f"Forced sentence buffer flush: '{sentence}'")
                return sentence

        return None

    def flush(self) -> Optional[str]:
        """Flush remaining text in buffer."""
        sentence = self._accumulator.strip()
        self._accumulator = ""
        if sentence:
            return sentence
        return None

    def clear(self) -> None:
        self._accumulator = ""

