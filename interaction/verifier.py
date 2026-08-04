import logging
from typing import Any, Dict

from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.Verifier")


class InteractionVerifier:
    async def verify_execution(
        self,
        goal: InteractionGoal,
        method: InteractionMethod,
        data: Dict[str, Any],
    ) -> bool:
        return True
