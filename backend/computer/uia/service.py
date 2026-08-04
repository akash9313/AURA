"""
UI Automation Service.
Central top-level service inheriting from core.service.Service.
Enables AURA to understand and interact with desktop applications semantically using UI Automation.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from core.service import Service
from computer.uia.actions import UIElementActionExecutor
from computer.uia.automation_provider import MicrosoftUIAutomationProvider
from computer.uia.automation_tree import UIAutomationTree
from computer.uia.cache import UIElementCache
from computer.uia.configuration import UIAutomationConfig
from computer.uia.events import UIAutomationEvent
from computer.uia.locator import UIElementLocator
from computer.uia.models import (
    AURAUIElement,
    ControlType,
    UIActionResult,
    UIElementQuery,
)
from computer.uia.verifier import UIElementVerifier

logger = logging.getLogger("AURA.Computer.UIA.Service")


class UIAutomationService(Service):
    """
    Central service wrapper exposing semantic UI Automation capabilities to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[UIAutomationConfig] = None,
    ):
        super().__init__(bus)
        self.config = config or UIAutomationConfig()
        self.provider = MicrosoftUIAutomationProvider()
        self.locator = UIElementLocator()
        self.executor = UIElementActionExecutor(bus=bus)
        self.cache = UIElementCache(config=self.config)
        self.verifier = UIElementVerifier()

        self._active_tree: Optional[UIAutomationTree] = None
        logger.info("UIAutomationService initialized")

    def get_automation_tree(self, target_window_title: Optional[str] = None, force_refresh: bool = False) -> UIAutomationTree:
        """
        Capture or retrieve the active UIAutomationTree hierarchy.

        Returns:
            UIAutomationTree instance.
        """
        if not self._active_tree or force_refresh:
            self._active_tree = self.provider.capture_tree_snapshot(target_window_title=target_window_title)
            self._publish_event(UIAutomationEvent.AUTOMATION_TREE_UPDATED, self._active_tree.root.to_dict())

        return self._active_tree

    def find_element(
        self,
        name: Optional[str] = None,
        automation_id: Optional[str] = None,
        control_type: Optional[ControlType] = None,
        target_window_title: Optional[str] = None,
    ) -> Optional[AURAUIElement]:
        """
        Find first matching element using smart caching and multi-strategy locator.
        Achieves sub-100ms lookup target.

        Returns:
            AURAUIElement if found, else None.
        """
        start_time = time.time()
        cache_key = f"{automation_id or ''}:{name or ''}:{control_type.value if control_type else ''}"

        # 1. Try cache
        cached = self.cache.get(cache_key)
        if cached:
            self._publish_event(UIAutomationEvent.CONTROL_FOUND, cached.to_dict())
            return cached

        # 2. Locate in tree
        tree = self.get_automation_tree(target_window_title=target_window_title)
        query = UIElementQuery(
            automation_id=automation_id,
            name=name,
            control_type=control_type,
            partial_match=True,
        )

        elem = self.locator.find_first_element(tree, query)
        if elem:
            self.cache.put(cache_key, elem)
            self._publish_event(UIAutomationEvent.CONTROL_FOUND, elem.to_dict())
            logger.info(f"Located element '{elem.name}' in {round((time.time() - start_time)*1000, 2)}ms")
            return elem

        self._publish_event(UIAutomationEvent.CONTROL_NOT_FOUND, {"query": cache_key})
        logger.warning(f"Failed to locate element matching '{cache_key}'")
        return None

    async def click(self, target: Union[AURAUIElement, str]) -> UIActionResult:
        """Click UI element by object reference or name query."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="click", message=f"Element '{target}' not found")
        return await self.executor.click(elem)

    async def invoke(self, target: Union[AURAUIElement, str]) -> UIActionResult:
        """Invoke UI element."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="invoke", message=f"Element '{target}' not found")
        return await self.executor.invoke(elem)

    async def type_text(self, target: Union[AURAUIElement, str], text: str) -> UIActionResult:
        """Type text into target UI control."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="type_text", message=f"Element '{target}' not found")
        return await self.executor.type_text(elem, text)

    async def expand(self, target: Union[AURAUIElement, str]) -> UIActionResult:
        """Expand UI control."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="expand", message=f"Element '{target}' not found")
        return await self.executor.expand(elem)

    async def collapse(self, target: Union[AURAUIElement, str]) -> UIActionResult:
        """Collapse UI control."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="collapse", message=f"Element '{target}' not found")
        return await self.executor.collapse(elem)

    async def focus(self, target: Union[AURAUIElement, str]) -> UIActionResult:
        """Focus UI control."""
        elem = target if isinstance(target, AURAUIElement) else self.find_element(name=target)
        if not elem:
            return UIActionResult(success=False, element_id="none", action="focus", message=f"Element '{target}' not found")
        return await self.executor.focus(elem)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting UIAutomationService...")

    def stop(self) -> None:
        logger.info("Stopping UIAutomationService...")
        self.cache.invalidate()

    def is_healthy(self) -> bool:
        return self.provider.is_healthy()

    def _publish_event(self, event: UIAutomationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish UIA event '{event.value}': {e}")
