"""
Retry Engine and Backoff Strategy Executor.
Implements Strategy Pattern for Exponential, Linear, Immediate, and Custom backoffs during retries.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Optional, Tuple

from browser.recovery.configuration import RecoveryConfig
from browser.recovery.models import BackoffStrategy

logger = logging.getLogger("AURA.Browser.Recovery.RetryEngine")


class RetryEngine:
    """
    Executes async operations with configurable retry policies and backoff strategies.
    """

    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()

    def calculate_delay_ms(
        self, attempt: int, strategy: Optional[BackoffStrategy] = None
    ) -> float:
        """
        Calculate backoff delay in milliseconds for a given attempt index (0-indexed).

        Args:
            attempt: Attempt count (0 for 1st retry, 1 for 2nd retry, etc.).
            strategy: BackoffStrategy enum override.

        Returns:
            Delay in milliseconds.
        """
        strat = strategy or self.config.default_backoff

        if strat == BackoffStrategy.IMMEDIATE:
            return 0.0

        if strat == BackoffStrategy.LINEAR:
            delay = self.config.initial_backoff_ms * (attempt + 1)
        else:  # EXPONENTIAL
            delay = self.config.initial_backoff_ms * (self.config.backoff_multiplier ** attempt)

        return min(delay, self.config.max_backoff_ms)

    async def execute_with_retry(
        self,
        func: Callable[[], Any],
        max_retries: Optional[int] = None,
        strategy: Optional[BackoffStrategy] = None,
        on_retry_callback: Optional[Callable[[int, Exception, float], None]] = None,
    ) -> Tuple[bool, Any, Optional[Exception], int]:
        """
        Execute an async callable with automatic retries and backoff delays.

        Returns:
            Tuple of (success, result_value, last_exception, attempts_made)
        """
        retries = max_retries if max_retries is not None else self.config.max_retries
        last_exception = None

        for attempt in range(retries + 1):
            if attempt > 0:
                delay_ms = self.calculate_delay_ms(attempt - 1, strategy=strategy)
                logger.info(f"Retry attempt {attempt}/{retries} waiting {delay_ms:.1f}ms...")

                if on_retry_callback:
                    try:
                        on_retry_callback(attempt, last_exception, delay_ms)
                    except Exception as e:
                        logger.debug(f"on_retry_callback error: {e}")

                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000)

            try:
                res = await func()
                return (True, res, None, attempt)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{retries + 1} failed: {e}")

        return (False, None, last_exception, retries)
