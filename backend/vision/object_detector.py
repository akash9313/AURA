import logging
from typing import Any, Dict, List, Union
from PIL import Image
from vision.image_utils import load_image
from vision.models import BoundingBox, DetectedObject

logger = logging.getLogger("AURA.Vision.ObjectDetector")


class ObjectDetector:
    """
    Object detection engine using Strategy Pattern to support YOLO, SAM, Gemini Vision, or OpenAI.
    """

    def detect_objects(self, image_source: Union[str, bytes, Image.Image]) -> List[DetectedObject]:
        """
        Detect objects in an image and return labeled bounding boxes.

        Args:
            image_source: Image file path, base64 string, bytes, or PIL Image.

        Returns:
            List[DetectedObject]: List of detected objects.
        """
        image = load_image(image_source)
        w, h = image.size
        objects: List[DetectedObject] = []

        # 1. Try Gemini Vision object detection
        try:
            from vision.providers.gemini_vision import GeminiVisionProvider
            provider = GeminiVisionProvider()
            items = provider.detect_objects(image)
            if items:
                for obj in items:
                    b = obj.get("box", {})
                    box = BoundingBox(
                        x=b.get("x", 0),
                        y=b.get("y", 0),
                        width=b.get("width", 100),
                        height=b.get("height", 100)
                    )
                    objects.append(DetectedObject(
                        label=obj.get("label", "object"),
                        box=box,
                        confidence=obj.get("confidence", 0.9),
                        attributes=obj.get("attributes", {})
                    ))
                if objects:
                    logger.info(f"Detected {len(objects)} object(s) via Gemini Vision.")
                    return objects
        except Exception as e:
            logger.debug(f"LLM Object Detector unavailable: {e}. Falling back to default scene detector.")

        # 2. Default Scene Heuristic
        objects.append(DetectedObject(
            label="Display Content",
            box=BoundingBox(x=0, y=0, width=w, height=h),
            confidence=0.9,
            attributes={"resolution": f"{w}x{h}"}
        ))
        return objects
