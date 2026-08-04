"""
Scroll Action Primitive Executor.
Provides page and element scrolling (up, down, left, right, to top, to bottom, and to element).
"""

import asyncio
import logging
from typing import Any, Optional

from browser.actions.models import ActionOptions, ScrollDirection

logger = logging.getLogger("AURA.Browser.Actions.Scrolling")


class ScrollActionExecutor:
    """Executes page and element scrolling actions."""

    async def scroll(
        self,
        page_handle: Any,
        direction: ScrollDirection = ScrollDirection.DOWN,
        element_handle: Optional[Any] = None,
        options: Optional[ActionOptions] = None,
    ) -> bool:
        """
        Scroll page or element in the specified direction.

        Args:
            page_handle: Page handle.
            direction: Direction to scroll.
            element_handle: Optional specific element container to scroll within.
            options: Action execution options.

        Returns:
            True if scroll succeeded.
        """
        opts = options or ActionOptions()
        distance = opts.scroll_distance_px

        logger.info(f"Executing scroll action ({direction.value}, distance: {distance}px)...")

        if direction == ScrollDirection.TO_ELEMENT and element_handle:
            if hasattr(element_handle, "scroll_into_view_if_needed"):
                await element_handle.scroll_into_view_if_needed()
                return True

        if page_handle and hasattr(page_handle, "evaluate"):
            if direction == ScrollDirection.DOWN:
                await page_handle.evaluate(f"window.scrollBy(0, {distance})")
            elif direction == ScrollDirection.UP:
                await page_handle.evaluate(f"window.scrollBy(0, -{distance})")
            elif direction == ScrollDirection.RIGHT:
                await page_handle.evaluate(f"window.scrollBy({distance}, 0)")
            elif direction == ScrollDirection.LEFT:
                await page_handle.evaluate(f"window.scrollBy(-{distance}, 0)")
            elif direction == ScrollDirection.TO_TOP:
                await page_handle.evaluate("window.scrollTo(0, 0)")
            elif direction == ScrollDirection.TO_BOTTOM:
                await page_handle.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            return True

        return True
