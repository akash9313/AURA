"""
Navigation Engine Core Navigator.
Orchestrates validation, actions, waits, retries, history tracking, and error recovery
into a single high-level navigation interface.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from browser.navigation.actions import NavigationActions
from browser.navigation.configuration import NavigationConfig
from browser.navigation.events import NavigationEvent
from browser.navigation.history import NavigationHistory
from browser.navigation.models import (
    NavigationActionType,
    NavigationErrorType,
    NavigationHealthStatus,
    NavigationHistoryInfo,
    NavigationResult,
    NavigationState,
    RedirectInfo,
    WaitStrategy,
)
from browser.navigation.validator import NavigationValidator
from browser.navigation.waits import WaitStrategyExecutor

logger = logging.getLogger("AURA.Browser.Navigation.Navigator")


class Navigator:
    """
    High-level Navigation Engine orchestrator.
    Composes NavigationActions, WaitStrategyExecutor, NavigationValidator, and NavigationHistory
    into a unified interface that the rest of AURA consumes.

    No Playwright objects are ever exposed. All methods return AURA abstractions.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[NavigationConfig] = None,
        page_resolver: Any = None,
    ):
        """
        Args:
            bus: AURA EventBus for publishing navigation events.
            config: Navigation configuration.
            page_resolver: Callable/object with get_page_handle(page_id) -> page_handle.
                           Injected by the NavigationService to decouple from Playwright.
        """
        self.bus = bus
        self.config = config or NavigationConfig()
        self.page_resolver = page_resolver

        self.actions = NavigationActions(config=self.config)
        self.waits = WaitStrategyExecutor(config=self.config)
        self.validator = NavigationValidator(config=self.config)
        self.history = NavigationHistory(config=self.config)

        self.state: NavigationState = NavigationState.IDLE

        # Telemetry
        self._total_navigations: int = 0
        self._successful_navigations: int = 0
        self._failed_navigations: int = 0
        self._total_load_time_ms: float = 0.0
        self._last_error: Optional[str] = None

    # ------------------------------------------------------------------
    # Page handle resolution
    # ------------------------------------------------------------------

    def _resolve_page_handle(self, page_id: Optional[str] = None) -> Any:
        """Resolve a page_id to its underlying page handle via the injected resolver."""
        if self.page_resolver is None:
            return None
        effective_id = page_id or self.config.default_page_id
        if effective_id is None:
            return None
        if callable(self.page_resolver):
            return self.page_resolver(effective_id)
        if hasattr(self.page_resolver, "get_page_handle"):
            return self.page_resolver.get_page_handle(effective_id)
        return None

    # ------------------------------------------------------------------
    # Primary navigation API
    # ------------------------------------------------------------------

    async def open_url(
        self,
        url: str,
        page_id: Optional[str] = None,
        wait_strategy: Optional[WaitStrategy] = None,
        selector: Optional[str] = None,
        timeout_ms: Optional[float] = None,
    ) -> NavigationResult:
        """
        Navigate a page to the given URL with validation, retries, wait strategy, and history tracking.
        """
        # Validate URL
        is_valid, error_type, error_msg = self.validator.validate_url(url)
        if not is_valid:
            logger.warning(f"URL validation failed: {error_msg}")
            return NavigationResult(
                success=False,
                url=url,
                error_type=error_type,
                error_message=error_msg,
                state=NavigationState.FAILED,
            )

        page_handle = self._resolve_page_handle(page_id)
        effective_page_id = page_id or self.config.default_page_id or "default"

        self.state = NavigationState.NAVIGATING
        self._publish_event(NavigationEvent.NAVIGATION_STARTED, {"url": url, "page_id": effective_page_id})

        # Retry loop
        last_result: Optional[NavigationResult] = None
        for attempt in range(self.config.retry_count + 1):
            if attempt > 0:
                delay = self.config.retry_delay_ms / 1000
                logger.info(f"Navigation retry {attempt}/{self.config.retry_count} for {url} (delay: {delay}s)")
                await asyncio.sleep(delay)

            result = await self.actions.open_url(page_handle, url, timeout_ms=timeout_ms)
            result.retry_count = attempt
            last_result = result

            if result.success:
                # Execute post-navigation wait strategy
                try:
                    wait_ms = await self.waits.execute_wait(
                        page_handle,
                        strategy=wait_strategy,
                        selector=selector,
                        timeout_ms=timeout_ms,
                    )
                    result.load_time_ms += wait_ms
                except asyncio.TimeoutError:
                    logger.warning(f"Wait strategy timed out after navigation to {url}")

                # Validate redirect chain
                if result.redirect_chain:
                    redirect_urls = [r.from_url for r in result.redirect_chain] + [result.url]
                    has_loop, loop_msg = self.validator.detect_redirect_loop(redirect_urls)
                    if has_loop:
                        result.success = False
                        result.error_type = NavigationErrorType.REDIRECT_LOOP
                        result.error_message = loop_msg
                        result.state = NavigationState.FAILED

                    ok, limit_msg = self.validator.validate_redirect_count(result.redirect_count)
                    if not ok:
                        result.success = False
                        result.error_type = NavigationErrorType.REDIRECT_LOOP
                        result.error_message = limit_msg
                        result.state = NavigationState.FAILED

                # Record in history
                self.history.record(
                    page_id=effective_page_id,
                    url=result.url or url,
                    title=result.title,
                    load_time_ms=result.load_time_ms,
                    action_type=NavigationActionType.OPEN_URL,
                    redirect_chain=result.redirect_chain,
                    success=result.success,
                    error=result.error_message,
                )

                self._record_telemetry(result)
                self.state = NavigationState.IDLE if result.success else NavigationState.FAILED

                event = NavigationEvent.NAVIGATION_COMPLETED if result.success else NavigationEvent.NAVIGATION_FAILED
                self._publish_event(event, result.to_dict())
                return result

            # If failed with non-retryable error, break immediately
            if result.error_type in (
                NavigationErrorType.INVALID_URL,
                NavigationErrorType.UNSUPPORTED_PROTOCOL,
                NavigationErrorType.REDIRECT_LOOP,
                NavigationErrorType.NAVIGATION_CANCELLED,
            ):
                break

        # All retries exhausted
        final = last_result or NavigationResult(
            success=False,
            url=url,
            error_type=NavigationErrorType.UNKNOWN,
            error_message="All retry attempts exhausted",
            state=NavigationState.FAILED,
        )

        self.history.record(
            page_id=effective_page_id,
            url=url,
            action_type=NavigationActionType.OPEN_URL,
            success=False,
            error=final.error_message,
        )

        self._record_telemetry(final)
        self.state = NavigationState.FAILED
        self._publish_event(NavigationEvent.NAVIGATION_FAILED, final.to_dict())
        return final

    async def reload(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Reload the current page."""
        page_handle = self._resolve_page_handle(page_id)
        effective_page_id = page_id or self.config.default_page_id or "default"

        result = await self.actions.reload(page_handle, timeout_ms=timeout_ms)

        self.history.record(
            page_id=effective_page_id,
            url=result.url,
            title=result.title,
            load_time_ms=result.load_time_ms,
            action_type=NavigationActionType.RELOAD,
            success=result.success,
            error=result.error_message,
        )

        self._record_telemetry(result)
        self._publish_event(NavigationEvent.PAGE_RELOADED, result.to_dict())
        return result

    async def go_back(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate back one step."""
        page_handle = self._resolve_page_handle(page_id)
        effective_page_id = page_id or self.config.default_page_id or "default"

        # Check AURA history first
        if not self.history.can_go_back(effective_page_id):
            logger.info(f"No back history available for page '{effective_page_id}'")
            return NavigationResult(
                success=False,
                error_type=NavigationErrorType.PAGE_LOAD_FAILURE,
                error_message="No back history available",
                state=NavigationState.FAILED,
            )

        result = await self.actions.go_back(page_handle, timeout_ms=timeout_ms)

        # Move the AURA history cursor
        entry = self.history.go_back(effective_page_id)
        if entry and result.success:
            result.url = result.url or entry.url
            result.title = result.title or entry.title

        self._record_telemetry(result)
        self._publish_event(NavigationEvent.PAGE_BACK, result.to_dict())
        return result

    async def go_forward(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate forward one step."""
        page_handle = self._resolve_page_handle(page_id)
        effective_page_id = page_id or self.config.default_page_id or "default"

        # Check AURA history first
        if not self.history.can_go_forward(effective_page_id):
            logger.info(f"No forward history available for page '{effective_page_id}'")
            return NavigationResult(
                success=False,
                error_type=NavigationErrorType.PAGE_LOAD_FAILURE,
                error_message="No forward history available",
                state=NavigationState.FAILED,
            )

        result = await self.actions.go_forward(page_handle, timeout_ms=timeout_ms)

        # Move the AURA history cursor
        entry = self.history.go_forward(effective_page_id)
        if entry and result.success:
            result.url = result.url or entry.url
            result.title = result.title or entry.title

        self._record_telemetry(result)
        self._publish_event(NavigationEvent.PAGE_FORWARD, result.to_dict())
        return result

    async def stop_loading(self, page_id: Optional[str] = None) -> NavigationResult:
        """Stop the current page from loading."""
        page_handle = self._resolve_page_handle(page_id)

        result = await self.actions.stop_loading(page_handle)
        self._publish_event(NavigationEvent.PAGE_STOPPED, result.to_dict())
        return result

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    async def current_url(self, page_id: Optional[str] = None) -> str:
        """Get the current URL of the page."""
        page_handle = self._resolve_page_handle(page_id)
        return await self.actions.get_current_url(page_handle)

    async def current_title(self, page_id: Optional[str] = None) -> str:
        """Get the current title of the page."""
        page_handle = self._resolve_page_handle(page_id)
        return await self.actions.get_current_title(page_handle)

    # ------------------------------------------------------------------
    # Wait API
    # ------------------------------------------------------------------

    async def wait_for_page_load(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for the page to finish loading."""
        page_handle = self._resolve_page_handle(page_id)
        wait_ms = await self.waits.wait_for_page_load(page_handle, timeout_ms=timeout_ms)
        self._publish_event(NavigationEvent.WAIT_COMPLETED, {"strategy": "load_event", "wait_ms": wait_ms})
        return wait_ms

    async def wait_for_network_idle(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for the network to become idle."""
        page_handle = self._resolve_page_handle(page_id)
        wait_ms = await self.waits.wait_for_network_idle(page_handle, timeout_ms=timeout_ms)
        self._publish_event(NavigationEvent.WAIT_COMPLETED, {"strategy": "network_idle", "wait_ms": wait_ms})
        return wait_ms

    async def wait_for_dom_ready(self, page_id: Optional[str] = None, timeout_ms: Optional[float] = None) -> float:
        """Wait for DOMContentLoaded."""
        page_handle = self._resolve_page_handle(page_id)
        wait_ms = await self.waits.wait_for_dom_ready(page_handle, timeout_ms=timeout_ms)
        self._publish_event(NavigationEvent.WAIT_COMPLETED, {"strategy": "dom_ready", "wait_ms": wait_ms})
        return wait_ms

    # ------------------------------------------------------------------
    # History API
    # ------------------------------------------------------------------

    def get_history_info(self, page_id: Optional[str] = None) -> NavigationHistoryInfo:
        """Get navigation history summary for a page."""
        effective_id = page_id or self.config.default_page_id or "default"
        return self.history.get_history_info(effective_id)

    # ------------------------------------------------------------------
    # Health / Telemetry
    # ------------------------------------------------------------------

    def get_health_status(self) -> NavigationHealthStatus:
        """Get current health telemetry for the Navigation Engine."""
        avg_load = (self._total_load_time_ms / self._total_navigations) if self._total_navigations > 0 else 0.0
        return NavigationHealthStatus(
            state=self.state,
            total_navigations=self._total_navigations,
            successful_navigations=self._successful_navigations,
            failed_navigations=self._failed_navigations,
            average_load_time_ms=round(avg_load, 2),
            active_page_id=self.config.default_page_id,
            last_error=self._last_error,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_telemetry(self, result: NavigationResult) -> None:
        """Update internal telemetry counters."""
        self._total_navigations += 1
        self._total_load_time_ms += result.load_time_ms
        if result.success:
            self._successful_navigations += 1
        else:
            self._failed_navigations += 1
            self._last_error = result.error_message

    def _publish_event(self, event: NavigationEvent, data: Dict[str, Any]) -> None:
        """Publish navigation event to the AURA EventBus."""
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish navigation event '{event.value}': {e}")
