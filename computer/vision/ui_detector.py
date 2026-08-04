import logging
import time
from typing import List, Optional

from computer.vision.detector import DefaultObjectDetector, VisualObjectDetector
from computer.vision.models import OCRResult, ScreenSnapshot, VisualElement, VisualElementType
from computer.vision.ocr import DefaultOCRProvider, OCRProvider

logger = logging.getLogger("AURA.Computer.Vision.UIDetector")


class UIDetector:
    def __init__(
        self,
        ocr_provider: Optional[OCRProvider] = None,
        object_detector: Optional[VisualObjectDetector] = None,
    ):
        self.ocr_provider = ocr_provider or DefaultOCRProvider()
        self.object_detector = object_detector or DefaultObjectDetector()

    async def analyze_snapshot(self, snapshot: ScreenSnapshot) -> ScreenSnapshot:
        ocr_results = await self.ocr_provider.extract_text(snapshot)
        visual_elements = await self.object_detector.detect_objects(snapshot)

        for ocr in ocr_results:
            text_elem = VisualElement(
                element_type=VisualElementType.TEXT,
                bounds=ocr.bounds,
                text=ocr.text,
                confidence=ocr.confidence,
            )
            visual_elements.append(text_elem)

        snapshot.ocr_results = ocr_results
        snapshot.visual_elements = visual_elements
        return snapshot
