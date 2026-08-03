import logging
from typing import Any, List, Optional, Union
from PIL import Image
from vision.image_utils import load_image, resize_image
from vision.models import VisionResult
from vision.object_detector import ObjectDetector
from vision.ocr import OCRModule
from vision.providers.base import BaseVisionProvider
from vision.providers.gemini_vision import GeminiVisionProvider
from vision.ui_detector import UIDetector

logger = logging.getLogger("AURA.Vision.Pipeline")


class VisionPipeline:
    """
    Modular Vision Pipeline coordinating multi-stage visual processing.

    Stages:
    1. Preprocessing (Resize/Format)
    2. OCR Text Extraction
    3. Object Detection
    4. UI Component Detection
    5. Vision LLM Multimodal Analysis
    6. Structured Result Synthesis
    """

    def __init__(
        self,
        provider: BaseVisionProvider = None,
        ocr: OCRModule = None,
        object_detector: ObjectDetector = None,
        ui_detector: UIDetector = None
    ):
        self.provider = provider if provider is not None else GeminiVisionProvider()
        self.ocr_module = ocr if ocr is not None else OCRModule()
        self.object_detector = object_detector if object_detector is not None else ObjectDetector()
        self.ui_detector = ui_detector if ui_detector is not None else UIDetector()

    def process(
        self,
        image_source: Union[str, bytes, Image.Image],
        prompt: str = "Describe this scene in detail.",
        enable_ocr: bool = True,
        enable_objects: bool = True,
        enable_ui: bool = True
    ) -> VisionResult:
        """
        Execute multi-stage processing on an input image.

        Args:
            image_source: Input image source (file path, bytes, or PIL Image).
            prompt: Text instruction or query for Vision LLM.
            enable_ocr: Whether to run OCR text extraction stage.
            enable_objects: Whether to run object detection stage.
            enable_ui: Whether to run UI element detection stage.

        Returns:
            VisionResult: Structured visual analysis result.
        """
        # 1. Preprocessing
        image = load_image(image_source)
        preprocessed = resize_image(image, max_dim=1024)

        # 2. OCR Stage
        ocr_result = None
        if enable_ocr:
            try:
                ocr_result = self.ocr_module.extract_text(preprocessed)
            except Exception as e:
                logger.error(f"Pipeline OCR stage error: {e}")

        # 3. Object Detection Stage
        objects = []
        if enable_objects:
            try:
                objects = self.object_detector.detect_objects(preprocessed)
            except Exception as e:
                logger.error(f"Pipeline Object Detection stage error: {e}")

        # 4. UI Detection Stage
        ui_elements = []
        if enable_ui:
            try:
                ui_elements = self.ui_detector.detect_ui_elements(preprocessed)
            except Exception as e:
                logger.error(f"Pipeline UI Detection stage error: {e}")

        # 5. Vision LLM Stage
        description = ""
        try:
            description = self.provider.analyze_image(preprocessed, prompt=prompt)
        except Exception as e:
            logger.error(f"Pipeline Vision LLM stage error: {e}")
            description = f"Scene containing {len(objects)} object(s) and {len(ui_elements)} UI element(s)."

        # 6. Structured Synthesis
        return VisionResult(
            description=description,
            objects=objects,
            detected_text=ocr_result,
            ui_elements=ui_elements,
            confidence=0.9,
            metadata={
                "provider": self.provider.name,
                "dimensions": f"{preprocessed.width}x{preprocessed.height}",
                "prompt": prompt
            }
        )
