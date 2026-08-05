import asyncio
import logging

logger = logging.getLogger("AURA.Workflow.Executor.Scheduler")


class ExecutionScheduler:
    def __init__(self, max_concurrency: int = 4):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def run_task(self, coro):
        async with self.semaphore:
            return await coro
