"""
Navigation Wait Strategies.
Strategy Pattern implementation for configurable page-load wait conditions.
"""

import asyncio
import logging
import time
from typing import Any, Optional

from browser.navigation.configuration import NavigationConfig
from browser.navigation.models import WaitStrategy

logger = logging.getLogger("AURA.Browser.Navigation.Waits")


class WaitStrategyExecutor:
    """
    Executes configurable wait strategies for page navigation.
    Abstracts Playwright wait primitives behind provider-independent interfaces.
    Uses Strategy Pattern to dispatch based on WaitStrategy enum.
    """

    def __init__(self, config: Optional[NavigationConfig] = None):
        self.config = config or NavigationConfig()
        self._strategy_dispatch = {
            WaitStrategy.DOM_READY: self._wait_dom_ready,
            WaitStrategy.LOAD_EVENT: self._wait_load_event,
            WaitStrategy.NETWORK_IDLE: self._wait_network_idle,
            WaitStrategy.CUSTOM_SELECTOR: self._wait_custom_selector,
            WaitStrategy.CUSTOM_TIMEOUT: self._wait_custom_timeout,
            WaitStrategy.NONE: self._wait_none,
        }

    async def execute_wait(
        self,
        page_handle: Any,
        strategy: Optional[WaitStrategy] = None,
        selector: Optional[str] = None,
        timeout_ms: Optional[float] = None,
    ) -> float:
        """
        Execute the specified wait strategy on a page handle.

        Args:
            page_handle: The Playwright page handle (or None for mock/fallback).
            strategy: The wait strategy to use. Defaults to config default.
            selector: CSS selector for CUSTOM_SELECTOR strategy.
            timeout_ms: Override timeout for CUSTOM_TIMEOUT strategy.

        Returns:
            Wait duration in milliseconds.
        """
        effective_strategy = strategy or self.config.default_wait_strategy
        handler = self._strategy_dispatch.get(effective_strategy, self._wait_load_event)

        logger.debug(f"Executing wait strategy: {effective_strategy.value}")
        start = time.time()

        try:
            await handler(page_handle, selector=selector, timeout_ms=timeout_ms)
        except asyncio.TimeoutError:
            logger.warning(f"Wait strategy '{effective_strategy.value}' timed out")
            raise
        except Exception as e:
            logger.warning(f"Wait strategy '{effective_strategy.value}' error: {e}")

        wait_ms = (time.time() - start) * 1000
        logger.debug(f"Wait strategy '{effective_strategy.value}' completed in {wait_ms:.1f}ms")
        return wait_ms

    async def _wait_dom_ready(self, page_handle: Any, **kwargs) -> None:
        """Wait for DOMContentLoaded event."""
        timeout = self.config.dom_ready_timeout_ms
        if page_handle and hasattr(page_handle, "wait_for_load_state"):
            await asyncio.wait_for(
                page_handle.wait_for_load_state("domcontentloaded"),
                timeout=timeout / 1000,
            )
        else:
            # Fallback for non-Playwright handles
            await asyncio.sleep(0.05)

    async def _wait_load_event(self, page_handle: Any, **kwargs) -> None:
        """Wait for the window load event."""
        timeout = self.config.navigation_timeout_ms
        if page_handle and hasattr(page_handle, "wait_for_load_state"):
            await asyncio.wait_for(
                page_handle.wait_for_load_state("load"),
                timeout=timeout / 1000,
            )
        else:
            await asyncio.sleep(0.05)

    async def _wait_network_idle(self, page_handle: Any, **kwargs) -> None:
        """Wait until the network becomes idle (no pending requests)."""
        timeout = self.config.network_idle_timeout_ms
        if page_handle and hasattr(page_handle, "wait_for_load_state"):
            await asyncio.wait_for(
                page_handle.wait_for_load_state("networkidle"),
                timeout=timeout / 1000,
            )
        else:
            await asyncio.sleep(0.05)

    async def _wait_custom_selector(self, page_handle: Any, selector: Optional[str] = None, **kwargs) -> None:
        """Wait for a specific CSS selector to appear in the DOM."""
        if not selector:
            logger.warning("CUSTOM_SELECTOR strategy requires a selector. Falling back to LOAD_EVENT.")
            await self._wait_load_event(page_handle)
            return

        timeout = self.config.custom_selector_timeout_ms
        if page_handle and hasattr(page_handle, "wait_for_selector"):
            await asyncio.wait_for(
                page_handle.wait_for_selector(selector),
                timeout=timeout / 1000,
            )
        else:
            await asyncio.sleep(0.05)

    async def _wait_custom_timeout(self, page_handle: Any, timeout_ms: Optional[float] = None, **kwargs) -> None:
        """Wait for a fixed timeout duration."""
        effective_timeout = timeout_ms or self.config.navigation_timeout_ms
        await asyncio.sleep(effective_timeout / 1000)

    async def _wait_none(self, page_handle: Any, **kwargs) -> None:
        """No-wait strategy for fire-and-forget navigations."""
        pass


    async def wait_for_page_load(self, page_handle: Any, timeout_ms: Optional[float] = None) -> float:
        """Convenience: wait for page load event."""
        return await self.execute_wait(
            page_handle,
            strategy=WaitStrategy.LOAD_EVENT,
            timeout_ms=timeout_ms,
        )

    async def wait_for_network_idle(self, page_handle: Any, timeout_ms: Optional[float] = None) -> float:
        """Convenience: wait for network idle."""
        return await self.execute_wait(
            page_handle,
            strategy=WaitStrategy.NETWORK_IDLE,
            timeout_ms=timeout_ms,
        )

    async def wait_for_dom_ready(self, page_handle: Any, timeout_ms: Optional[float] = None) -> float:
        """Convenience: wait for DOMContentLoaded."""
        return await self.execute_wait(
            page_handle,
            strategy=WaitStrategy.DOM_READY,
            timeout_ms=timeout_ms,
        )
