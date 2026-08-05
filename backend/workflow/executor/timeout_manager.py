"""
Workflow Timeout Manager.
Enforces task and workflow level execution timeouts using asyncio.wait_for.
"""

import asyncio
import logging
from typing import Any, Awaitable, TypeVar

logger = logging.getLogger("AURA.Workflow.Executor.Timeout")

T = TypeVar("T")


class TimeoutManager:
    """
    Manages timeout boundaries for asynchronous execution tasks.
    """

    async def execute_with_timeout(self, coro: Awaitable[T], timeout_sec: float) -> T:
        """
        Execute coroutine with specified timeout.

        Args:
            coro: Async coroutine to execute.
            timeout_sec: Timeout boundary in seconds.

        Returns:
            Result of coroutine.

        Raises:
            asyncio.TimeoutError if timeout_sec is exceeded.
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"Execution timed out after {timeout_sec}s")
            raise
