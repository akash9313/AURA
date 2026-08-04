import abc
import logging
import time
from typing import List

from computer.vision.models import OCRResult, ScreenSnapshot

logger = logging.getLogger("AURA.Computer.Vision.OCR")


class OCRProvider(abc.ABC):
    @abc.abstractmethod
    async def extract_text(self, snapshot: ScreenSnapshot) -> List[OCRResult]:
        pass


class DefaultOCRProvider(OCRProvider):
    async def extract_text(self, snapshot: ScreenSnapshot) -> List[OCRResult]:
        return [
            OCRResult(text="File", bounds=(10, 30, 40, 20), confidence=0.98),
            OCRResult(text="Edit", bounds=(60, 30, 40, 20), confidence=0.97),
            OCRResult(text="View", bounds=(110, 30, 40, 20), confidence=0.96),
            OCRResult(text="Submit", bounds=(520, 150, 100, 30), confidence=0.99),
            OCRResult(text="Cancel", bounds=(630, 150, 100, 30), confidence=0.95),
        ]
