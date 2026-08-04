"""
Form-Specific Action Primitive Executor.
Provides dropdown selection, checkbox toggling, and form submission execution.
"""

import logging
from typing import Any, Optional

from browser.actions.models import ActionOptions

logger = logging.getLogger("AURA.Browser.Actions.Forms")


class FormActionExecutor:
    """Executes dropdown selection, checkbox toggling, and form submission."""

    async def select_dropdown(
        self, element_handle: Any, option_value_or_label: str, options: Optional[ActionOptions] = None
    ) -> bool:
        """Select an option in a <select> element by value or visible label."""
        opts = options or ActionOptions()
        logger.info(f"Executing select_dropdown option '{option_value_or_label}'...")

        if element_handle and hasattr(element_handle, "select_option"):
            try:
                await element_handle.select_option(value=option_value_or_label, timeout=opts.timeout_ms)
                return True
            except Exception:
                await element_handle.select_option(label=option_value_or_label, timeout=opts.timeout_ms)
                return True

        return True

    async def check_checkbox(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Check a checkbox element if not already checked."""
        opts = options or ActionOptions()
        logger.info("Executing check_checkbox...")

        if element_handle and hasattr(element_handle, "check"):
            await element_handle.check(force=opts.force, timeout=opts.timeout_ms)
            return True

        return True

    async def uncheck_checkbox(self, element_handle: Any, options: Optional[ActionOptions] = None) -> bool:
        """Uncheck a checkbox element if currently checked."""
        opts = options or ActionOptions()
        logger.info("Executing uncheck_checkbox...")

        if element_handle and hasattr(element_handle, "uncheck"):
            await element_handle.uncheck(force=opts.force, timeout=opts.timeout_ms)
            return True

        return True

    async def submit_form(
        self, element_or_form_handle: Any, options: Optional[ActionOptions] = None
    ) -> bool:
        """Submit a form element or click its submit button."""
        opts = options or ActionOptions()
        logger.info("Executing submit_form...")

        if element_or_form_handle and hasattr(element_or_form_handle, "evaluate"):
            try:
                await element_or_form_handle.evaluate("el => el.form ? el.form.submit() : el.submit()")
                return True
            except Exception:
                if hasattr(element_or_form_handle, "click"):
                    await element_or_form_handle.click(force=opts.force, timeout=opts.timeout_ms)
                    return True

        return True
