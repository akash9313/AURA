"""
Navigation Actions Executor.
Provider-independent browser navigation action primitives (open_url, reload, go_back, go_forward, stop_loading).
"""

import asyncio
import logging
import time
from typing import Any, Optional

from browser.navigation.configuration import NavigationConfig
from browser.navigation.models import (
    NavigationActionType,
    NavigationErrorType,
    NavigationResult,
    NavigationState,
    RedirectInfo,
)

logger = logging.getLogger("AURA.Browser.Navigation.Actions")


class NavigationActions:
    """
    Executes atomic navigation actions against a page handle.
    Abstracts Playwright navigation primitives behind provider-independent interfaces.
    Every method returns a NavigationResult; no Playwright objects are ever exposed.
    """

    def __init__(self, config: Optional[NavigationConfig] = None):
        self.config = config or NavigationConfig()

    async def open_url(self, page_handle: Any, url: str, timeout_ms: Optional[float] = None) -> NavigationResult:
        """
        Navigate a page to the specified URL.

        Args:
            page_handle: Provider page handle (Playwright page or mock).
            url: Target URL.
            timeout_ms: Override navigation timeout.

        Returns:
            NavigationResult with success status, final URL, title, and timing.
        """
        effective_timeout = timeout_ms or self.config.navigation_timeout_ms
        start = time.time()

        logger.info(f"Navigation open_url: {url} (timeout: {effective_timeout}ms)")

        if page_handle and hasattr(page_handle, "goto"):
            try:
                response = await asyncio.wait_for(
                    page_handle.goto(url, wait_until="load"),
                    timeout=effective_timeout / 1000,
                )
                final_url = page_handle.url if hasattr(page_handle, "url") else url
                title = ""
                if hasattr(page_handle, "title"):
                    title = await page_handle.title() if asyncio.iscoroutinefunction(page_handle.title) else page_handle.title()

                load_time_ms = (time.time() - start) * 1000

                # Collect redirect chain from response headers if available
                redirect_chain = []
                if response and hasattr(response, "request") and hasattr(response.request, "redirected_from"):
                    req = response.request.redirected_from
                    while req:
                        redirect_chain.insert(0, RedirectInfo(
                            from_url=req.url,
                            to_url=final_url,
                            status_code=0,
                        ))
                        req = req.redirected_from if hasattr(req, "redirected_from") else None

                logger.info(f"Navigation open_url completed: {final_url} in {load_time_ms:.1f}ms")
                return NavigationResult(
                    success=True,
                    url=final_url,
                    title=title,
                    load_time_ms=load_time_ms,
                    redirect_count=len(redirect_chain),
                    redirect_chain=redirect_chain,
                    state=NavigationState.COMPLETED,
                )

            except asyncio.TimeoutError:
                load_time_ms = (time.time() - start) * 1000
                logger.error(f"Navigation open_url timed out after {load_time_ms:.1f}ms: {url}")
                return NavigationResult(
                    success=False,
                    url=url,
                    load_time_ms=load_time_ms,
                    error_type=NavigationErrorType.TIMEOUT,
                    error_message=f"Navigation timed out after {effective_timeout}ms",
                    state=NavigationState.TIMED_OUT,
                )
            except Exception as e:
                load_time_ms = (time.time() - start) * 1000
                error_type = self._classify_error(e)
                logger.error(f"Navigation open_url failed: {e}")
                return NavigationResult(
                    success=False,
                    url=url,
                    load_time_ms=load_time_ms,
                    error_type=error_type,
                    error_message=str(e),
                    state=NavigationState.FAILED,
                )
        else:
            # Fallback for non-Playwright / mock handles
            load_time_ms = (time.time() - start) * 1000
            return NavigationResult(
                success=True,
                url=url,
                title="",
                load_time_ms=load_time_ms,
                state=NavigationState.COMPLETED,
            )

    async def reload(self, page_handle: Any, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Reload the current page."""
        effective_timeout = timeout_ms or self.config.navigation_timeout_ms
        start = time.time()

        logger.info("Navigation reload requested")

        if page_handle and hasattr(page_handle, "reload"):
            try:
                await asyncio.wait_for(
                    page_handle.reload(),
                    timeout=effective_timeout / 1000,
                )
                url = page_handle.url if hasattr(page_handle, "url") else ""
                title = ""
                if hasattr(page_handle, "title"):
                    title = await page_handle.title() if asyncio.iscoroutinefunction(page_handle.title) else page_handle.title()

                load_time_ms = (time.time() - start) * 1000
                logger.info(f"Navigation reload completed: {url} in {load_time_ms:.1f}ms")
                return NavigationResult(
                    success=True,
                    url=url,
                    title=title,
                    load_time_ms=load_time_ms,
                    state=NavigationState.COMPLETED,
                )
            except asyncio.TimeoutError:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=NavigationErrorType.TIMEOUT,
                    error_message=f"Reload timed out after {effective_timeout}ms",
                    state=NavigationState.TIMED_OUT,
                )
            except Exception as e:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=self._classify_error(e),
                    error_message=str(e),
                    state=NavigationState.FAILED,
                )
        else:
            load_time_ms = (time.time() - start) * 1000
            return NavigationResult(success=True, load_time_ms=load_time_ms, state=NavigationState.COMPLETED)

    async def go_back(self, page_handle: Any, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate the page back one step in browser history."""
        effective_timeout = timeout_ms or self.config.navigation_timeout_ms
        start = time.time()

        logger.info("Navigation go_back requested")

        if page_handle and hasattr(page_handle, "go_back"):
            try:
                await asyncio.wait_for(
                    page_handle.go_back(),
                    timeout=effective_timeout / 1000,
                )
                url = page_handle.url if hasattr(page_handle, "url") else ""
                title = ""
                if hasattr(page_handle, "title"):
                    title = await page_handle.title() if asyncio.iscoroutinefunction(page_handle.title) else page_handle.title()

                load_time_ms = (time.time() - start) * 1000
                logger.info(f"Navigation go_back completed: {url}")
                return NavigationResult(
                    success=True,
                    url=url,
                    title=title,
                    load_time_ms=load_time_ms,
                    state=NavigationState.COMPLETED,
                )
            except asyncio.TimeoutError:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=NavigationErrorType.TIMEOUT,
                    error_message=f"Go back timed out after {effective_timeout}ms",
                    state=NavigationState.TIMED_OUT,
                )
            except Exception as e:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=self._classify_error(e),
                    error_message=str(e),
                    state=NavigationState.FAILED,
                )
        else:
            load_time_ms = (time.time() - start) * 1000
            return NavigationResult(success=True, load_time_ms=load_time_ms, state=NavigationState.COMPLETED)

    async def go_forward(self, page_handle: Any, timeout_ms: Optional[float] = None) -> NavigationResult:
        """Navigate the page forward one step in browser history."""
        effective_timeout = timeout_ms or self.config.navigation_timeout_ms
        start = time.time()

        logger.info("Navigation go_forward requested")

        if page_handle and hasattr(page_handle, "go_forward"):
            try:
                await asyncio.wait_for(
                    page_handle.go_forward(),
                    timeout=effective_timeout / 1000,
                )
                url = page_handle.url if hasattr(page_handle, "url") else ""
                title = ""
                if hasattr(page_handle, "title"):
                    title = await page_handle.title() if asyncio.iscoroutinefunction(page_handle.title) else page_handle.title()

                load_time_ms = (time.time() - start) * 1000
                logger.info(f"Navigation go_forward completed: {url}")
                return NavigationResult(
                    success=True,
                    url=url,
                    title=title,
                    load_time_ms=load_time_ms,
                    state=NavigationState.COMPLETED,
                )
            except asyncio.TimeoutError:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=NavigationErrorType.TIMEOUT,
                    error_message=f"Go forward timed out after {effective_timeout}ms",
                    state=NavigationState.TIMED_OUT,
                )
            except Exception as e:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=self._classify_error(e),
                    error_message=str(e),
                    state=NavigationState.FAILED,
                )
        else:
            load_time_ms = (time.time() - start) * 1000
            return NavigationResult(success=True, load_time_ms=load_time_ms, state=NavigationState.COMPLETED)

    async def stop_loading(self, page_handle: Any) -> NavigationResult:
        """Stop the current page from loading."""
        start = time.time()

        logger.info("Navigation stop_loading requested")

        if page_handle and hasattr(page_handle, "evaluate"):
            try:
                await page_handle.evaluate("window.stop()")
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=True,
                    load_time_ms=load_time_ms,
                    state=NavigationState.CANCELLED,
                )
            except Exception as e:
                load_time_ms = (time.time() - start) * 1000
                return NavigationResult(
                    success=False,
                    load_time_ms=load_time_ms,
                    error_type=NavigationErrorType.NAVIGATION_CANCELLED,
                    error_message=str(e),
                    state=NavigationState.FAILED,
                )
        else:
            load_time_ms = (time.time() - start) * 1000
            return NavigationResult(success=True, load_time_ms=load_time_ms, state=NavigationState.CANCELLED)

    async def get_current_url(self, page_handle: Any) -> str:
        """Get the current URL of the page."""
        if page_handle and hasattr(page_handle, "url"):
            return page_handle.url
        return ""

    async def get_current_title(self, page_handle: Any) -> str:
        """Get the current title of the page."""
        if page_handle and hasattr(page_handle, "title"):
            try:
                title = page_handle.title()
                if asyncio.iscoroutine(title):
                    title = await title
                return title or ""
            except Exception:
                return ""
        return ""

    def _classify_error(self, error: Exception) -> NavigationErrorType:
        """Classify an exception into a NavigationErrorType."""
        msg = str(error).lower()

        if "dns" in msg or "name resolution" in msg or "getaddrinfo" in msg:
            return NavigationErrorType.DNS_FAILURE
        if "ssl" in msg or "certificate" in msg or "cert" in msg:
            return NavigationErrorType.SSL_ERROR
        if "timeout" in msg:
            return NavigationErrorType.TIMEOUT
        if "crash" in msg or "target closed" in msg or "browser has been closed" in msg:
            return NavigationErrorType.BROWSER_CRASH
        if "cancel" in msg or "aborted" in msg:
            return NavigationErrorType.NAVIGATION_CANCELLED
        if "net::err" in msg:
            return NavigationErrorType.PAGE_LOAD_FAILURE

        return NavigationErrorType.UNKNOWN
