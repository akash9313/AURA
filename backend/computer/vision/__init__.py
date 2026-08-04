"""
AURA Screen Intelligence Subsystem.
Provides visual understanding of desktop screens independent of UI Automation APIs.
"""

from computer.vision.detector import DefaultObjectDetector, VisualObjectDetector
from computer.vision.events import ScreenVisionEvent
from computer.vision.layout import LayoutNode, ScreenLayoutAnalyzer
from computer.vision.models import (
    OCRResult,
    ScreenSnapshot,
    VisualElement,
    VisualElementType,
    VisualVerificationResult,
)
from computer.vision.ocr import DefaultOCRProvider, OCRProvider
from computer.vision.screen_capture import ScreenCaptureEngine
from computer.vision.screenshot_cache import ScreenshotCache
from computer.vision.service import ScreenIntelligenceService
from computer.vision.ui_detector import UIDetector

__all__ = [
    "ScreenIntelligenceService",
    "ScreenCaptureEngine",
    "UIDetector",
    "ScreenLayoutAnalyzer",
    "LayoutNode",
    "ScreenshotCache",
    "OCRProvider",
    "DefaultOCRProvider",
    "VisualObjectDetector",
    "DefaultObjectDetector",
    "VisualElement",
    "VisualElementType",
    "OCRResult",
    "ScreenSnapshot",
    "VisualVerificationResult",
    "ScreenVisionEvent",
]
