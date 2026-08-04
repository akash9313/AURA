import logging
import time
from typing import List, Optional

from interaction.confidence import InteractionConfidenceScorer
from interaction.configuration import InteractionEngineConfig
from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.Planner")

PRIORITY_ORDER = [
    InteractionMethod.UI_AUTOMATION,
    InteractionMethod.BROWSER_DOM,
    InteractionMethod.KEYBOARD,
    InteractionMethod.MOUSE,
    InteractionMethod.VISION,
]


class InteractionPlanner:
    def __init__(self, config: Optional[InteractionEngineConfig] = None):
        self.config = config or InteractionEngineConfig()
        self.scorer = InteractionConfidenceScorer()

    def plan_interaction(self, goal: InteractionGoal) -> List[InteractionMethod]:
        start_time = time.time()
        scores = self.scorer.score_methods(goal)

        candidates = sorted(
            PRIORITY_ORDER,
            key=lambda m: (scores.get(m, 0.0), -PRIORITY_ORDER.index(m)),
            reverse=True,
        )

        return candidates
