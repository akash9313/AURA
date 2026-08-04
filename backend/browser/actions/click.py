"""
Click, Hover, Focus, and Drag & Drop Action Primitive Executor.
Provides provider-independent execution for click, double click, right click, hover, focus, blur, and drag-and-drop.
"""

import asyncio
import logging
from typing import Any, Optional

from browser.actions.models import ActionOptions

logger = logging.getLogger("AURA.Browser.Actions.Click")


class ClickActionExecutor:
    """Executes click, hover, focus, blur, and drag-and-drop primitives."""

    async def click(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Perform click action."""
        opts = options or ActionOptions()
        logger.info("Executing click action...")
        if element_handle and hasattr(element_handle, "click"):
            await element_handle.click(force=opts.force, timeout=opts.timeout_ms)
            return True
        return True

    async def double_click(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Perform double click action."""
        opts = options or ActionOptions()
        logger.info("Executing double click action...")
        if element_handle and hasattr(element_handle, "dblclick"):
            await element_handle.dblclick(force=opts.force, timeout=opts.timeout_ms)
            return True
        elif element_handle and hasattr(element_handle, "click"):
            await element_handle.click(click_count=2, force=opts.force, timeout=opts.timeout_ms)
            return True
        return True

    async def right_click(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Perform context/right click action."""
        opts = options or ActionOptions()
        logger.info("Executing right click action...")
        if element_handle and hasattr(element_handle, "click"):
            await element_handle.click(button="right", force=opts.force, timeout=opts.timeout_ms)
            return True
        return True

    async def hover(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Perform hover action over element."""
        opts = options or ActionOptions()
        logger.info("Executing hover action...")
        if element_handle and hasattr(element_handle, "hover"):
            await element_handle.hover(force=opts.force, timeout=opts.timeout_ms)
            return True
        return True

    async def focus(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Set focus on element."""
        logger.info("Executing focus action...")
        if element_handle and hasattr(element_handle, "focus"):
            await element_handle.focus(timeout=options.timeout_ms if options else 30000.0)
            return True
        return True

    async def blur(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Remove focus (blur) from element."""
        logger.info("Executing blur action...")
        if element_handle and hasattr(element_handle, "evaluate"):
            await element_handle.evaluate("el => el.blur()")
            return True
        return True

    async def drag_and_drop(
        self, source_handle: Any, target_handle: Any, options: Optional[ActionOptions] = None
    ) -> bool:
        """Perform drag and drop from source element to target element."""
        opts = options or ActionOptions()
        logger.info("Executing drag and drop action...")
        if source_handle and hasattr(source_handle, "drag_to") and target_handle:
            await source_handle.drag_to(target_handle, timeout=opts.timeout_ms)
            return True
        return True
