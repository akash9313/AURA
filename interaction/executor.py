import logging
import time
from typing import Any, Dict, Optional

from interaction.configuration import InteractionEngineConfig
from interaction.events import InteractionEvent
from interaction.fallback import FallbackManager
from interaction.models import (
    InteractionGoal,
    InteractionMethod,
    InteractionResult,
)
from interaction.planner import InteractionPlanner
from interaction.strategy import (
    BrowserDOMStrategy,
    InteractionStrategy,
    KeyboardStrategy,
    MouseStrategy,
    UIAutomationStrategy,
    VisionStrategy,
)
from interaction.verifier import InteractionVerifier

logger = logging.getLogger("AURA.Interaction.Executor")


class InteractionExecutor:
    def __init__(
        self,
        bus: Any = None,
        config: Optional[InteractionEngineConfig] = None,
    ):
        self.bus = bus
        self.config = config or InteractionEngineConfig()

        self.planner = InteractionPlanner(config=self.config)
        self.fallback = FallbackManager(bus=bus)
        self.verifier = InteractionVerifier()

        self._strategy_map: Dict[InteractionMethod, InteractionStrategy] = {
            InteractionMethod.UI_AUTOMATION: UIAutomationStrategy(),
            InteractionMethod.BROWSER_DOM: BrowserDOMStrategy(),
            InteractionMethod.KEYBOARD: KeyboardStrategy(),
            InteractionMethod.MOUSE: MouseStrategy(),
            InteractionMethod.VISION: VisionStrategy(),
        }

    async def execute_goal(self, goal: InteractionGoal) -> InteractionResult:
        start_time = time.time()
        self._publish_event(InteractionEvent.INTERACTION_STARTED, goal.to_dict())

        candidates = self.planner.plan_interaction(goal)
        fallback_count = 0

        while candidates:
            current_method = candidates.pop(0)
            self._publish_event(
                InteractionEvent.METHOD_SELECTED,
                {"goal_id": goal.goal_id, "method": current_method.value},
            )

            strategy = self._strategy_map.get(current_method)
            if not strategy:
                continue

            try:
                ok, msg, data = await strategy.execute(goal)

                if ok and self.config.auto_verify:
                    ok = await self.verifier.verify_execution(goal, current_method, data)

                if ok:
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    res = InteractionResult(
                        success=True,
                        method_used=current_method,
                        confidence=0.95,
                        fallback_count=fallback_count,
                        duration_ms=duration_ms,
                        message=msg,
                        data=data,
                    )
                    self._publish_event(InteractionEvent.INTERACTION_COMPLETED, res.to_dict())
                    return res

                fallback_count += 1
                next_method = self.fallback.handle_method_failure(goal, current_method, msg, candidates)
                if not next_method:
                    break

            except Exception as e:
                fallback_count += 1
                next_method = self.fallback.handle_method_failure(goal, current_method, str(e), candidates)
                if not next_method:
                    break

        duration_ms = round((time.time() - start_time) * 1000, 2)
        res = InteractionResult(
            success=False,
            method_used=InteractionMethod.VISION,
            confidence=0.0,
            fallback_count=fallback_count,
            duration_ms=duration_ms,
            message="All interaction strategies failed",
        )
        self._publish_event(InteractionEvent.METHOD_FAILED, res.to_dict())
        return res

    def _publish_event(self, event: InteractionEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish interaction event '{event.value}': {e}")
