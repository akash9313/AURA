from abc import ABC, abstractmethod
from typing import Optional

from wakeword.configuration import WakeWordConfig
from wakeword.models import WakeWordDetectionResult


class BaseWakeWordProvider(ABC):
    def __init__(self, config: WakeWordConfig):
        self.config = config

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def process_frame(self, pcm_chunk: bytes) -> WakeWordDetectionResult:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
