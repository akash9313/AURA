import os
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image, ImageDraw
from tools.registry import ToolRegistry
from vision.image_utils import create_fallback_image
from vision.manager import VisionManager
from vision.models import VisionResult
from vision.ocr import OCRModule
from vision.pipeline import VisionPipeline
from vision.screenshot import ScreenshotManager
from vision.ui_detector import UIDetector


class TestVisionEngine(unittest.TestCase):

    def setUp(self):
        # Create a sample test image for testing
        self.temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        self.temp_img.close()

        img = Image.new("RGB", (400, 300), color=(50, 100, 150))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "AURA Vision Test", fill=(255, 255, 255))
        img.save(self.temp_img.name)

        self.vision_mgr = VisionManager()

    def tearDown(self):
        if os.path.exists(self.temp_img.name):
            os.remove(self.temp_img.name)

    def test_image_loading_and_fallback(self):
        img = self.vision_mgr.read_image(self.temp_img.name)
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (400, 300))

        fallback = create_fallback_image("Test Canvas", size=(200, 200))
        self.assertEqual(fallback.size, (200, 200))

    def test_screenshot_manager(self):
        sct_mgr = ScreenshotManager()
        path = sct_mgr.capture_full_screen()
        self.assertTrue(os.path.exists(path))
        if os.path.exists(path):
            os.remove(path)

    def test_ocr_extraction(self):
        ocr = OCRModule()
        result = ocr.extract_text(self.temp_img.name)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.full_text)

    def test_ui_element_detection(self):
        ui_det = UIDetector()
        elements = ui_det.detect_ui_elements(self.temp_img.name)
        self.assertGreater(len(elements), 0)
        types = [e.element_type for e in elements]
        self.assertIn("window", types)

    @patch("ai.llm.ask_ai", return_value="Mocked Vision LLM Analysis Response")
    def test_vision_pipeline_processing(self, mock_ask_ai):
        pipeline = VisionPipeline()
        res = pipeline.process(self.temp_img.name, prompt="Analyze image test")
        self.assertIsInstance(res, VisionResult)
        self.assertIsNotNone(res.description)
        self.assertGreater(len(res.objects), 0)

    @patch("ai.llm.ask_ai", return_value="Mocked Vision Manager Analysis Response")
    def test_vision_manager_analyze_image(self, mock_ask_ai):
        res = self.vision_mgr.analyze_image(self.temp_img.name, prompt="Describe scene")
        self.assertIsInstance(res, VisionResult)
        self.assertIn("description", res.to_dict())

    def test_vision_tools_auto_discovery(self):
        registry = ToolRegistry(auto_discover=True)
        tools = registry.list_tools()
        self.assertIn("analyze_image", tools)
        self.assertIn("read_screen", tools)
        self.assertIn("read_document", tools)
        self.assertIn("capture_screenshot", tools)
        self.assertIn("camera_capture", tools)


if __name__ == "__main__":
    unittest.main()
