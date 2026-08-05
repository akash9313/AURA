"""
Base Wake Word Provider Interface.
Abstract base class for wake word detection providers (OpenWakeWord, Porcupine, Custom ONNX).
"""

from abc import ABC, abstractmethod
from typing import Optional

from wakeword.configuration import WakeWordConfig
from wakeword.models import WakeWordDetectionResult


class BaseWakeWordProvider(ABC):
    """
    Provider abstraction interface for wake word detection engines.
    """

    def __init__(self, config: WakeWordConfig):
        self.config = config

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize provider models and runtime resources."""
        pass

    @abstractmethod
    def process_frame(self, pcm_chunk: bytes) -> WakeWordDetectionResult:
        """
        Process a single PCM audio frame and return detection result.

        Args:
            pcm_chunk: Raw 16kHz 16-bit mono PCM bytes.

        Returns:
            WakeWordDetectionResult object.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier name."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Release provider resources."""
        pass
