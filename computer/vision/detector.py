import abc
import logging
import time
from typing import List

from computer.vision.models import ScreenSnapshot, VisualElement, VisualElementType

logger = logging.getLogger("AURA.Computer.Vision.Detector")


class VisualObjectDetector(abc.ABC):
    @abc.abstractmethod
    async def detect_objects(self, snapshot: ScreenSnapshot) -> List[VisualElement]:
        pass


class DefaultObjectDetector(VisualObjectDetector):
    async def detect_objects(self, snapshot: ScreenSnapshot) -> List[VisualElement]:
        return [
            VisualElement(
                element_type=VisualElementType.BUTTON,
                bounds=(520, 150, 100, 30),
                text="Submit",
                confidence=0.98,
            ),
            VisualElement(
                element_type=VisualElementType.BUTTON,
                bounds=(630, 150, 100, 30),
                text="Cancel",
                confidence=0.95,
            ),
            VisualElement(
                element_type=VisualElementType.TOOLBAR,
                bounds=(0, 25, 1920, 35),
                confidence=0.99,
            ),
            VisualElement(
                element_type=VisualElementType.STATUSBAR,
                bounds=(0, 1050, 1920, 30),
                confidence=0.99,
            ),
        ]
