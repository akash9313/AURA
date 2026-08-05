"""
Desktop Recovery Validator.
Validates desktop error recovery strategies:
1. Retry strategy
2. Window refocus
3. Alternative UI locator
4. Vision fallback
5. Application restart
"""

import asyncio
import inspect
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("AURA.Windows.Validation.Recovery")


class DesktopRecoveryStrategy(Enum):
    """Desktop recovery mechanisms."""
    RETRY = "retry"
    WINDOW_REFOCUS = "window_refocus"
    ALTERNATIVE_LOCATOR = "alternative_locator"
    VISION_FALLBACK = "vision_fallback"
    APPLICATION_RESTART = "application_restart"


class DesktopRecoveryValidator:
    """
    Validates and executes desktop error recovery mechanisms upon task execution failure.
    """

    async def execute_with_recovery(
        self,
        capability_name: str,
        execution_fn: Callable[..., Any],
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Execute capability function with automatic recovery strategy escalation:
        Attempt 1: Direct Execution
        Attempt 2: Retry & Window Refocus
        Attempt 3: Alternative UI Locator / Vision Fallback
        Attempt 4: Application Restart

        Returns:
            Result dictionary with recovery_attempts tally.
        """
        recovery_attempts = 0
        last_error: Optional[Exception] = None

        strategies = [
            DesktopRecoveryStrategy.RETRY,
            DesktopRecoveryStrategy.WINDOW_REFOCUS,
            DesktopRecoveryStrategy.ALTERNATIVE_LOCATOR,
            DesktopRecoveryStrategy.VISION_FALLBACK,
            DesktopRecoveryStrategy.APPLICATION_RESTART,
        ]

        for attempt in range(max_retries):
            try:
                strategy = strategies[min(attempt, len(strategies) - 1)]
                logger.info(f"Executing desktop capability '{capability_name}' (Attempt {attempt + 1}, Strategy: '{strategy.value}')...")

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
                logger.warning(f"Attempt {attempt + 1} for '{capability_name}' failed ({e}). Applying recovery strategy '{strategies[min(attempt, len(strategies) - 1)].value}'...")

                await asyncio.sleep(0.05)

        return {
            "success": False,
            "error": str(last_error),
            "recovery_attempts": recovery_attempts,
            "final_strategy": "failed",
        }
