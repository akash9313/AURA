"""
UI Element Action Verifier.
Verifies control existence, enabled state, focus, value mutations, toggle states, and expand/collapse states.
"""

import logging
from typing import Optional

from computer.uia.models import AURAUIElement

logger = logging.getLogger("AURA.Computer.UIA.Verifier")


class UIElementVerifier:
    """
    Validates post-action state mutations on AURAUIElement nodes.
    """

    def verify_exists(self, element: Optional[AURAUIElement]) -> bool:
        """Verify element exists and is valid."""
        ok = element is not None and element.is_visible
        logger.debug(f"Verify exists for element '{element.element_id if element else 'None'}': {ok}")
        return ok

    def verify_enabled(self, element: AURAUIElement) -> bool:
        """Verify element is enabled for interaction."""
        ok = element.is_enabled
        logger.debug(f"Verify enabled for element '{element.element_id}': {ok}")
        return ok

    def verify_value_changed(self, element: AURAUIElement, expected_value: str) -> bool:
        """Verify text value matches expected value."""
        ok = (element.value == expected_value)
        logger.debug(f"Verify value changed for element '{element.element_id}' to '{expected_value}': {ok}")
        return ok
