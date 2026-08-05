import asyncio
import inspect
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("AURA.Browser.Validation.Recovery")


class RecoveryStrategy(Enum):
    RETRY = "retry"
    ALTERNATIVE_LOCATOR = "alternative_locator"
    REFRESH = "refresh"
    BROWSER_RESTART = "browser_restart"


class BrowserRecoveryValidator:
    async def execute_with_recovery(
        self,
        capability_name: str,
        execution_fn: Callable[..., Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        recovery_attempts = 0
        last_error: Optional[Exception] = None

        strategies = [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.ALTERNATIVE_LOCATOR,
            RecoveryStrategy.REFRESH,
            RecoveryStrategy.BROWSER_RESTART,
        ]

        for attempt in range(max_retries):
            try:
                strategy = strategies[min(attempt, len(strategies) - 1)]

                if inspect.iscoroutinefunction(execution_fn):
                    res = await execution_fn()
                else:
                    res = execution_fn()

                if isinstance(res, dict) and res.get("status") == "failed":
                    raise RuntimeError(res.get("error", "Execution returned failed status"))

                return {
                    "success": True,
                    "result": res,
                    "recovery_attempts": recovery_attempts,
                    "final_strategy": strategy.value if recovery_attempts > 0 else "none",
                }

            except Exception as e:
                last_error = e
                recovery_attempts += 1
                await asyncio.sleep(0.05)

        return {
            "success": False,
            "error": str(last_error),
            "recovery_attempts": recovery_attempts,
            "final_strategy": "failed",
        }
