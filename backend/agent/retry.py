import logging
import time
from typing import Callable, Any

logger = logging.getLogger("AURA.Agent.Retry")


class RetryStrategy:
    """
    Configurable exponential backoff retry handler for failed tasks.
    """

    def __init__(self, max_retries: int = 3, initial_delay: float = 0.5, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def get_delay(self, retry_count: int) -> float:
        """Calculate exponential backoff delay in seconds."""
        return self.initial_delay * (self.backoff_factor ** retry_count)

    def execute_with_retry(self, action: Callable[[], Any], task_id: str = "task") -> Any:
        """
        Execute an action with automatic exponential backoff retries.

        Args:
            action (Callable): Function to execute.
            task_id (str): Identifier for logging.

        Returns:
            Any: Result of the action function.
        """
        attempt = 0
        while True:
            try:
                return action()
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    logger.error(f"Task '{task_id}' failed after {attempt} attempt(s): {e}")
                    raise e

                delay = self.get_delay(attempt - 1)
                logger.warning(f"Task '{task_id}' attempt {attempt} failed ({e}). Retrying in {delay:.2f}s...")
                time.sleep(delay)
