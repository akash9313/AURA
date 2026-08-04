"""
Screen Intelligence Engine Unit & Integration Tests.
Covers vision domain models, sub-100ms screen capture engine, OCR strategy provider,
object detector strategy provider, UI detector fusion, screen layout composite hierarchy,
visual action verifier, and ScreenIntelligenceService integration.
"""

import asyncio
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from computer.vision.models import (
    OCRResult,
    ScreenSnapshot,
    VisualElement,
    VisualElementType,
    VisualVerificationResult,
)
from computer.vision.events import ScreenVisionEvent
from computer.vision.screenshot_cache import ScreenshotCache
from computer.vision.screen_capture import ScreenCaptureEngine
from computer.vision.ocr import DefaultOCRProvider
from computer.vision.detector import DefaultObjectDetector
from computer.vision.ui_detector import UIDetector
from computer.vision.layout import ScreenLayoutAnalyzer
from computer.vision.service import ScreenIntelligenceService


# ==============================================================================
# Domain Models & Cache Tests
# ==============================================================================

class TestVisionModelsAndCache(unittest.TestCase):
    """Tests for vision domain models and frame buffer cache."""

    def test_visual_element_serialization(self):
        elem = VisualElement(
            element_type=VisualElementType.BUTTON,
            bounds=(100, 100, 80, 30),
            text="OK",
            confidence=0.99,
        )
        d = elem.to_dict()
        self.assertEqual(d["element_type"], "button")
        self.assertEqual(d["text"], "OK")

    def test_screenshot_cache_hashing(self):
        cache = ScreenshotCache()
        snap1 = ScreenSnapshot(bounds=(0, 0, 1920, 1080), timestamp=100.0)
        h1 = cache.put(snap1)

        self.assertIsNotNone(h1)
        self.assertTrue(cache.is_identical(h1))

        snap2 = ScreenSnapshot(bounds=(0, 0, 1920, 1080), timestamp=200.0)
        h2 = cache.put(snap2)
        self.assertTrue(cache.is_identical(h2))


# ==============================================================================
# Screen Capture & Detector Strategy Tests
# ==============================================================================

class TestScreenCaptureAndDetectors(unittest.TestCase):
    """Tests for sub-100ms capture engine, OCR, and Object Detection strategy providers."""

    def setUp(self):
        self.capture = ScreenCaptureEngine()
        self.ocr = DefaultOCRProvider()
        self.detector = DefaultObjectDetector()
        self.ui_detector = UIDetector(ocr_provider=self.ocr, object_detector=self.detector)

    def test_sub_100ms_desktop_capture(self):
        start = time.time()
        snap = asyncio.run(self.capture.capture_desktop())
        duration_ms = (time.time() - start) * 1000

        self.assertIsNotNone(snap)
        self.assertLess(duration_ms, 100.0)

    def test_ui_detector_fusion(self):
        snap = asyncio.run(self.capture.capture_desktop())
        analyzed = asyncio.run(self.ui_detector.analyze_snapshot(snap))

        self.assertGreater(len(analyzed.ocr_results), 0)
        self.assertGreater(len(analyzed.visual_elements), 0)


# ==============================================================================
# Layout Hierarchy & Service Integration Tests
# ==============================================================================

class TestScreenIntelligenceServiceIntegration(unittest.TestCase):
    """Integration tests for ScreenIntelligenceService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = ScreenIntelligenceService(bus=self.bus)

    def test_layout_composite_tree(self):
        snap = asyncio.run(self.service.capture_desktop())
        analyzed = asyncio.run(self.service.analyze_screen(snap))
        tree = self.service.get_layout_tree(analyzed)

        self.assertEqual(tree.name, "Desktop")
        self.assertEqual(tree.children[0].name, "Primary Monitor")

    def test_visual_verification(self):
        before_snap = asyncio.run(self.service.capture_desktop())
        res = asyncio.run(self.service.verify_action_visuals(before_snap, "click_submit_button"))

        self.assertIsNotNone(res)
        self.assertEqual(res.action_name, "click_submit_button")
        self.bus.publish.assert_called()


if __name__ == "__main__":
    unittest.main()
