import logging
from typing import Any, Dict, List, Optional

from interaction.events import InteractionEvent
from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.Fallback")


class FallbackManager:
    def __init__(self, bus: Any = None):
        self.bus = bus

    def handle_method_failure(
        self,
        goal: InteractionGoal,
        failed_method: InteractionMethod,
        reason: str,
        remaining_candidates: List[InteractionMethod],
    ) -> Optional[InteractionMethod]:
        self._publish_event(
            InteractionEvent.METHOD_FAILED,
            {"goal_id": goal.goal_id, "failed_method": failed_method.value, "reason": reason},
        )

        if not remaining_candidates:
            return None

        next_method = remaining_candidates[0]
        self._publish_event(
            InteractionEvent.METHOD_SWITCHED,
            {"goal_id": goal.goal_id, "from": failed_method.value, "to": next_method.value},
        )

        return next_method

    def _publish_event(self, event: InteractionEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish interaction event '{event.value}': {e}")
