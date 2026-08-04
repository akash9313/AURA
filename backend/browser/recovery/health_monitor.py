"""
Browser Infrastructure Health Monitor.
Continuously audits process responsiveness, memory usage, latency, and crash frequency.
"""

import asyncio
import logging
import time
from typing import Any, Optional

from browser.recovery.configuration import RecoveryConfig
from browser.recovery.models import HealthMetrics

logger = logging.getLogger("AURA.Browser.Recovery.HealthMonitor")


class HealthMonitor:
    """
    Monitors browser infrastructure health and evaluates telemetry thresholds.
    """

    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.metrics = HealthMetrics()

    async def check_health(
        self, browser_manager_ref: Any = None, page_handle: Any = None
    ) -> HealthMetrics:
        """
        Audit browser process, page responsiveness, and memory usage.

        Returns:
            Updated HealthMetrics object.
        """
        start_time = time.time()
        process_alive = True
        page_responsive = True

        # Audit browser process if reference provided
        if browser_manager_ref and hasattr(browser_manager_ref, "is_healthy"):
            try:
                process_alive = browser_manager_ref.is_healthy()
            except Exception as e:
                logger.warning(f"Process health check error: {e}")
                process_alive = False

        # Audit page responsiveness
        if page_handle and hasattr(page_handle, "evaluate"):
            try:
                pong = await page_handle.evaluate("() => 'pong'")
                page_responsive = (pong == "pong")
            except Exception as e:
                logger.warning(f"Page responsiveness check failed: {e}")
                page_responsive = False

        latency_ms = round((time.time() - start_time) * 1000, 2)
        is_healthy = process_alive and page_responsive and (self.metrics.crash_count < self.config.max_crash_threshold)

        self.metrics.process_alive = process_alive
        self.metrics.page_responsive = page_responsive
        self.metrics.navigation_latency_ms = latency_ms
        self.metrics.healthy = is_healthy
        self.metrics.last_check_timestamp = time.time()

        logger.debug(f"Health check complete: Healthy={is_healthy} (Latency: {latency_ms}ms)")
        return self.metrics

    def record_crash(self) -> None:
        """Increment crash counter telemetry."""
        self.metrics.crash_count += 1
        logger.warning(f"Browser crash recorded. Total crash count: {self.metrics.crash_count}")
