"""
Workflow Concurrency & Execution Scheduler.
Enforces parallel concurrency limits via asyncio.Semaphore during workflow execution.
"""

import asyncio
import logging

logger = logging.getLogger("AURA.Workflow.Executor.Scheduler")


class ExecutionScheduler:
    """
    Manages concurrency limits for parallel task execution.
    """

    def __init__(self, max_concurrency: int = 4):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def run_task(self, coro):
        """Execute coroutine bounded by concurrency semaphore."""
        async with self.semaphore:
            return await coro
