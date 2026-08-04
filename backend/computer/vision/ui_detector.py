"""
UI Detector Fusion Engine.
Fuses OCR text bounds and visual object detection bounding boxes into unified visual element nodes.
"""

import logging
import time
from typing import List, Optional

from computer.vision.detector import DefaultObjectDetector, VisualObjectDetector
from computer.vision.models import OCRResult, ScreenSnapshot, VisualElement, VisualElementType
from computer.vision.ocr import DefaultOCRProvider, OCRProvider

logger = logging.getLogger("AURA.Computer.Vision.UIDetector")


class UIDetector:
    """
    Fuses OCR and Object Detection model results into structured visual elements.
    """

    def __init__(
        self,
        ocr_provider: Optional[OCRProvider] = None,
        object_detector: Optional[VisualObjectDetector] = None,
    ):
        self.ocr_provider = ocr_provider or DefaultOCRProvider()
        self.object_detector = object_detector or DefaultObjectDetector()

    async def analyze_snapshot(self, snapshot: ScreenSnapshot) -> ScreenSnapshot:
        """
        Run OCR extraction and Object Detection over ScreenSnapshot frame.

        Returns:
            Mutated ScreenSnapshot with populated visual_elements and ocr_results.
        """
        start_time = time.time()

        ocr_results = await self.ocr_provider.extract_text(snapshot)
        visual_elements = await self.object_detector.detect_objects(snapshot)

        # Merge OCR text into visual element text nodes
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

        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Analyzed screen snapshot '{snapshot.snapshot_id}' in {duration_ms}ms ({len(visual_elements)} elements)")
        return snapshot
