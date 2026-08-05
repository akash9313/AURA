import asyncio
import logging
from typing import Any, Awaitable, TypeVar

logger = logging.getLogger("AURA.Workflow.Executor.Timeout")

T = TypeVar("T")


class TimeoutManager:
    async def execute_with_timeout(self, coro: Awaitable[T], timeout_sec: float) -> T:
        try:
            return await asyncio.wait_for(coro, timeout=timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"Execution timed out after {timeout_sec}s")
            raise
