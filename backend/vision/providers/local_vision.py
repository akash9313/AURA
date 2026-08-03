import logging
from typing import Any, Dict, List
from PIL import Image
from vision.providers.base import BaseVisionProvider

logger = logging.getLogger("AURA.Vision.Providers.Local")


class LocalVisionProvider(BaseVisionProvider):
    """
    Multimodal Vision Provider utilizing local open-weights vision models (LLaVA, Qwen-VL, Moondream).
    """

    @property
    def name(self) -> str:
        return "local"

    def analyze_image(self, image: Image.Image, prompt: str = "Describe this image in detail.") -> str:
        logger.info("LocalVisionProvider analyzing image...")
        return f"[Local Vision LLM] Scene analysis for image ({image.width}x{image.height})."

    def ocr(self, image: Image.Image) -> str:
        return f"Local OCR text from image ({image.width}x{image.height})"

    def detect_ui(self, image: Image.Image) -> List[Dict[str, Any]]:
        return []

    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        return []
