from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PIL import Image


class BaseVisionProvider(ABC):
    """
    Abstract Base Class for Multimodal Vision LLM Providers.
    
    Decouples vision LLM models (Gemini, OpenAI, Local models) from core vision services.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier name (e.g. 'gemini', 'openai', 'local')."""
        pass

    @abstractmethod
    def analyze_image(self, image: Image.Image, prompt: str = "Describe this image in detail.") -> str:
        """
        Analyze an image with a specific text prompt.

        Args:
            image (PIL.Image): Image instance.
            prompt (str): Prompt instruction.

        Returns:
            str: Multimodal LLM text response.
        """
        pass

    @abstractmethod
    def ocr(self, image: Image.Image) -> str:
        """Perform text extraction via Multimodal Vision LLM."""
        pass

    @abstractmethod
    def detect_ui(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect UI components via Multimodal Vision LLM."""
        pass

    @abstractmethod
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect scene objects via Multimodal Vision LLM."""
        pass
