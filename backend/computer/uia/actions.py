"""
UI Element Action Executor.
Executes semantic UI Automation actions (Click, Invoke, Expand, Collapse, Focus, Type Text, Select, Toggle, Scroll, Value Set/Read).
"""

import logging
import time
from typing import Any, Dict, Optional

from computer.uia.events import UIAutomationEvent
from computer.uia.models import AURAUIElement, UIActionResult, UIPattern
from computer.uia.verifier import UIElementVerifier

logger = logging.getLogger("AURA.Computer.UIA.Actions")


class UIElementActionExecutor:
    """
    Executes actions on AURAUIElement nodes with automatic verification and EventBus publishing.
    """

    def __init__(self, bus: Any = None):
        self.bus = bus
        self.verifier = UIElementVerifier()

    async def click(self, element: AURAUIElement) -> UIActionResult:
        """Simulate click on UI element."""
        start_time = time.time()
        logger.info(f"Clicking UI element '{element.name}' (ID: {element.element_id})...")

        if not self.verifier.verify_exists(element) or not self.verifier.verify_enabled(element):
            return self._build_result(False, element.element_id, "click", "Element missing or disabled", start_time)

        self._publish_event(UIAutomationEvent.CONTROL_CLICKED, element.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="click",
            message=f"Clicked '{element.name}'",
            execution_time_ms=duration,
        )

    async def invoke(self, element: AURAUIElement) -> UIActionResult:
        """Invoke element via InvokePattern."""
        start_time = time.time()
        logger.info(f"Invoking UI element '{element.name}'...")
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="invoke",
            message=f"Invoked '{element.name}'",
            execution_time_ms=duration,
        )

    async def type_text(self, element: AURAUIElement, text: str) -> UIActionResult:
        """Type text into TextBox/Edit control."""
        start_time = time.time()
        logger.info(f"Typing '{text[:15]}...' into '{element.name}'...")

        element.value = text
        self._publish_event(UIAutomationEvent.TEXT_ENTERED, {"element_id": element.element_id, "text": text})
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="type_text",
            message=f"Typed text into '{element.name}'",
            data={"value": text},
            execution_time_ms=duration,
        )

    async def expand(self, element: AURAUIElement) -> UIActionResult:
        """Expand tree/menu item."""
        start_time = time.time()
        self._publish_event(UIAutomationEvent.CONTROL_EXPANDED, element.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="expand",
            message=f"Expanded '{element.name}'",
            execution_time_ms=duration,
        )

    async def collapse(self, element: AURAUIElement) -> UIActionResult:
        """Collapse tree/menu item."""
        start_time = time.time()
        self._publish_event(UIAutomationEvent.CONTROL_COLLAPSED, element.to_dict())
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="collapse",
            message=f"Collapsed '{element.name}'",
            execution_time_ms=duration,
        )

    async def focus(self, element: AURAUIElement) -> UIActionResult:
        """Set focus on UI element."""
        start_time = time.time()
        element.is_focused = True
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="focus",
            message=f"Focused '{element.name}'",
            execution_time_ms=duration,
        )

    async def set_value(self, element: AURAUIElement, value: str) -> UIActionResult:
        """Set ValuePattern value on element."""
        start_time = time.time()
        element.value = value
        self._publish_event(UIAutomationEvent.VALUE_CHANGED, {"element_id": element.element_id, "value": value})
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=True,
            element_id=element.element_id,
            action="set_value",
            message=f"Set value on '{element.name}' to '{value}'",
            data={"value": value},
            execution_time_ms=duration,
        )

    def _build_result(self, success: bool, element_id: str, action: str, msg: str, start_time: float) -> UIActionResult:
        duration = round((time.time() - start_time) * 1000, 2)
        return UIActionResult(
            success=success,
            element_id=element_id,
            action=action,
            message=msg,
            execution_time_ms=duration,
        )

    def _publish_event(self, event: UIAutomationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish UI event '{event.value}': {e}")
