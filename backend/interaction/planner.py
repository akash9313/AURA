"""
Interaction Planner Decision Engine.
Selects optimal interaction method under 20ms using priority ordering and confidence scoring.
Priority: UI Automation (1) -> Browser DOM (2) -> Keyboard (3) -> Mouse (4) -> Vision (5).
"""

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
    """
    Sub-20ms decision engine for interaction method selection.
    """

    def __init__(self, config: Optional[InteractionEngineConfig] = None):
        self.config = config or InteractionEngineConfig()
        self.scorer = InteractionConfidenceScorer()

    def plan_interaction(self, goal: InteractionGoal) -> List[InteractionMethod]:
        """
        Determine prioritized ordered list of candidate interaction methods for execution and fallback.
        Ensures decision executes under 20 ms.

        Args:
            goal: InteractionGoal request.

        Returns:
            Ordered List of InteractionMethod candidates.
        """
        start_time = time.time()
        scores = self.scorer.score_methods(goal)

        # Sort priority order based on highest confidence score while respecting base priority order
        candidates = sorted(
            PRIORITY_ORDER,
            key=lambda m: (scores.get(m, 0.0), -PRIORITY_ORDER.index(m)),
            reverse=True,
        )

        duration_ms = (time.time() - start_time) * 1000
        logger.debug(f"Planned interaction methods {candidates} in {round(duration_ms, 3)}ms (Target: <20ms)")
        return candidates
