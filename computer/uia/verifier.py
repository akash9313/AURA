import logging
from typing import Optional

from computer.uia.models import AURAUIElement

logger = logging.getLogger("AURA.Computer.UIA.Verifier")


class UIElementVerifier:
    def verify_exists(self, element: Optional[AURAUIElement]) -> bool:
        return element is not None and element.is_visible

    def verify_enabled(self, element: AURAUIElement) -> bool:
        return element.is_enabled

    def verify_value_changed(self, element: AURAUIElement, expected_value: str) -> bool:
        return element.value == expected_value
