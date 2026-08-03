import logging
from typing import Any, Dict, List, Optional, Union
from PIL import Image
from vision.analyzer import VisionAnalyzer
from vision.barcode import BarcodeDetector
from vision.camera import CameraManager
from vision.document import DocumentAnalyzer
from vision.image_utils import load_image
from vision.models import (
    DetectedObject,
    DocumentAnalysisResult,
    OCRResult,
    UIElement,
    VisionResult,
)
from vision.ocr import OCRModule
from vision.pipeline import VisionPipeline
from vision.providers.base import BaseVisionProvider
from vision.providers.gemini_vision import GeminiVisionProvider
from vision.screenshot import ScreenshotManager
from vision.ui_detector import UIDetector

logger = logging.getLogger("AURA.Vision.Manager")


class VisionManager:
    """
    Central Entry Point for the AURA Vision Engine.

    Coordinates Screenshot Capture, Camera Capture, OCR, UI Detection, Object Detection,
    Document Analysis, and Multimodal LLM Vision Processing.
    """

    def __init__(self, provider: BaseVisionProvider = None):
        self.provider = provider if provider is not None else GeminiVisionProvider()
        self.screenshot_mgr = ScreenshotManager()
        self.camera_mgr = CameraManager()
        self.ocr_module = OCRModule()
        self.ui_detector = UIDetector()
        self.doc_analyzer = DocumentAnalyzer(ocr=self.ocr_module)
        self.barcode_detector = BarcodeDetector()
        self.pipeline = VisionPipeline(provider=self.provider, ocr=self.ocr_module, ui_detector=self.ui_detector)
        self.analyzer = VisionAnalyzer(pipeline=self.pipeline)
        logger.info("VisionManager initialized successfully.")

    # --- Screen & Camera Capture API ---
    def capture_screen(self, region: Tuple[int, int, int, int] = None) -> str:
        """Capture desktop screen or specified sub-region. Returns image file path."""
        if region:
            x, y, w, h = region
            return self.screenshot_mgr.capture_region(x, y, w, h)
        return self.screenshot_mgr.capture_full_screen()

    def capture_camera(self, device_id: int = 0) -> str:
        """Capture image frame from camera device. Returns image file path."""
        return self.camera_mgr.capture_image(device_id=device_id)

    # --- Core Vision Analysis API ---
    def read_image(self, source: Union[str, bytes, Image.Image]) -> Image.Image:
        """Load and return PIL RGB Image from file path, bytes, or base64 string."""
        return load_image(source)

    def analyze_image(self, source: Union[str, bytes, Image.Image], prompt: str = "Describe this image in detail.") -> VisionResult:
        """Execute full multi-stage Vision Pipeline analysis on an image."""
        return self.pipeline.process(source, prompt=prompt)

    def ocr(self, source: Union[str, bytes, Image.Image]) -> OCRResult:
        """Extract text tokens and bounding boxes from an image."""
        return self.ocr_module.extract_text(source)

    def detect_objects(self, source: Union[str, bytes, Image.Image]) -> List[DetectedObject]:
        """Detect objects in an image."""
        return self.pipeline.object_detector.detect_objects(source)

    def detect_ui(self, source: Union[str, bytes, Image.Image]) -> List[UIElement]:
        """Detect UI components in an image for desktop automation."""
        return self.ui_detector.detect_ui_elements(source)

    def read_pdf_page(self, pdf_path: str) -> DocumentAnalysisResult:
        """Extract text and document elements from a PDF document."""
        return self.doc_analyzer.analyze_document(pdf_path)

    def describe_scene(self, source: Union[str, bytes, Image.Image]) -> str:
        """Get human-readable text description of an image scene."""
        result = self.analyze_image(source)
        return result.description
