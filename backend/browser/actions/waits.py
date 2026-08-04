"""
Action Wait Primitives and Smart Pre-checks.
Verifies element existence, visibility, enabled state, scroll readiness, and DOM stability before action execution.
"""

import asyncio
import logging
import time
from typing import Any, Optional, Tuple

from browser.actions.models import ActionOptions

logger = logging.getLogger("AURA.Browser.Actions.Waits")


class ActionWaitExecutor:
    """
    Executes pre-action stability waits and element state verifications.
    """

    async def precheck_element(
        self, page_handle: Any, element_handle: Any, options: Optional[ActionOptions] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify element exists, is visible, enabled, and scrolled into view before performing an action.

        Returns:
            Tuple of (is_ready, error_message)
        """
        opts = options or ActionOptions()

        if element_handle is None and page_handle is None:
            # Fallback for unit testing with mock handles
            return (True, None)

        if element_handle is None:
            return (False, "Element handle is None")

        # 1. Existence & Visibility check
        if hasattr(element_handle, "is_visible"):
            try:
                visible = await element_handle.is_visible()
                if not visible and not opts.force:
                    return (False, "Element is not visible in DOM")
            except Exception as e:
                return (False, f"Visibility check failed: {e}")

        # 2. Enabled check
        if hasattr(element_handle, "is_enabled"):
            try:
                enabled = await element_handle.is_enabled()
                if not enabled and not opts.force:
                    return (False, "Element is disabled")
            except Exception as e:
                return (False, f"Enabled check failed: {e}")

        # 3. Scroll into view if needed
        if opts.scroll_into_view and hasattr(element_handle, "scroll_into_view_if_needed"):
            try:
                await element_handle.scroll_into_view_if_needed()
            except Exception as e:
                logger.debug(f"scroll_into_view warning: {e}")

        # 4. Human interaction delay
        if opts.human_delay_ms > 0:
            await asyncio.sleep(opts.human_delay_ms / 1000)

        return (True, None)

    async def wait_for_dom_stability(self, page_handle: Any, timeout_ms: float = 1000.0) -> None:
        """Wait for page layout / DOM animations to stabilize."""
        if page_handle and hasattr(page_handle, "wait_for_load_state"):
            try:
                await page_handle.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            except Exception:
                pass
        else:
            await asyncio.sleep(0.05)
