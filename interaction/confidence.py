import logging
from typing import Dict

from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.ConfidenceScorer")

METHOD_RELIABILITY = {
    InteractionMethod.UI_AUTOMATION: 0.98,
    InteractionMethod.BROWSER_DOM: 0.95,
    InteractionMethod.KEYBOARD: 0.90,
    InteractionMethod.MOUSE: 0.85,
    InteractionMethod.VISION: 0.80,
    InteractionMethod.CLIPBOARD: 0.95,
}


class InteractionConfidenceScorer:
    def score_methods(self, goal: InteractionGoal) -> Dict[InteractionMethod, float]:
        scores = {}
        target = goal.target

        if target.automation_id or target.name:
            scores[InteractionMethod.UI_AUTOMATION] = 0.98
        else:
            scores[InteractionMethod.UI_AUTOMATION] = 0.50

        if target.selector or (target.name and "http" in (target.name or "").lower()):
            scores[InteractionMethod.BROWSER_DOM] = 0.95
        else:
            scores[InteractionMethod.BROWSER_DOM] = 0.40

        if goal.intent.value in ("type", "copy", "paste", "save"):
            scores[InteractionMethod.KEYBOARD] = 0.92
        else:
            scores[InteractionMethod.KEYBOARD] = 0.60

        if target.coordinates or target.name:
            scores[InteractionMethod.MOUSE] = 0.85
        else:
            scores[InteractionMethod.MOUSE] = 0.50

        scores[InteractionMethod.VISION] = 0.80

        if goal.preferred_method and goal.preferred_method in scores:
            scores[goal.preferred_method] = 0.99

        return scores
