"""
Text Typing, Clearing, Pasting, and Keyboard Shortcut Executor.
Handles text input with human-like typing delays, field clearing, clipboards, and keyboard shortcuts.
"""

import asyncio
import logging
from typing import Any, Optional

from browser.actions.models import ActionOptions

logger = logging.getLogger("AURA.Browser.Actions.Typing")


class TypingActionExecutor:
    """Executes text typing, clearing, pasting, and keyboard shortcut actions."""

    async def type_text(
        self, element_handle: Any, text: str, options: Optional[ActionOptions] = None
    ) -> bool:
        """Type text into element with optional human typing delay per character."""
        opts = options or ActionOptions()
        logger.info(f"Executing type_text action ('{text[:20]}...')...")

        if element_handle and hasattr(element_handle, "type"):
            delay_ms = (1000.0 / opts.typing_speed_cps) if opts.typing_speed_cps > 0 else 0.0
            await element_handle.type(text, delay=delay_ms, timeout=opts.timeout_ms)
            return True
        elif element_handle and hasattr(element_handle, "fill"):
            await element_handle.fill(text, timeout=opts.timeout_ms)
            return True

        return True

    async def clear_field(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Clear text input or textarea field."""
        opts = options or ActionOptions()
        logger.info("Executing clear_field action...")

        if element_handle and hasattr(element_handle, "fill"):
            await element_handle.fill("", timeout=opts.timeout_ms)
            return True
        elif element_handle and hasattr(element_handle, "evaluate"):
            await element_handle.evaluate("el => { el.value = ''; }")
            return True

        return True

    async def paste(self, element_handle: Any, text: str, options: Optional[ActionOptions] = None) -> bool:
        """Paste text into element (instant fill without keystroke simulation)."""
        opts = options or ActionOptions()
        logger.info(f"Executing paste action ('{text[:20]}...')...")

        if element_handle and hasattr(element_handle, "fill"):
            await element_handle.fill(text, timeout=opts.timeout_ms)
            return True

        return True

    async def press_shortcut(
        self, page_handle: Any, key_combination: str, options: Optional[ActionOptions] = None
    ) -> bool:
        """Press keyboard shortcut or key (e.g. 'Control+A', 'Enter', 'Tab', 'Escape')."""
        opts = options or ActionOptions()
        logger.info(f"Executing press_shortcut key combination: '{key_combination}'...")

        if page_handle and hasattr(page_handle, "keyboard"):
            await page_handle.keyboard.press(key_combination, timeout=opts.timeout_ms)
            return True

        return True
