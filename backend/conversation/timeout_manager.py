"""
Conversation Timeout Manager.
Enforces follow-up timeouts, max conversation duration limits, and silence timeout boundaries.
"""

import asyncio
import logging
from typing import Awaitable, TypeVar

from conversation.configuration import ConversationConfig

logger = logging.getLogger("AURA.Conversation.Timeout")

T = TypeVar("T")


class ConversationTimeoutManager:
    """
    Manages timeout boundaries for voice conversation operations.
    """

    def __init__(self, config: ConversationConfig):
        self.config = config

    async def execute_with_timeout(self, coro: Awaitable[T], timeout_sec: float) -> T:
        """
        Execute coroutine bounded by timeout.
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"Conversation operation timed out after {timeout_sec}s")
            raise
