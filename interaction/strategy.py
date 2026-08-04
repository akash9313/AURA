import abc
import logging
import time
from typing import Any, Dict, Tuple

from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.Strategy")


class InteractionStrategy(abc.ABC):
    @abc.abstractmethod
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        pass


class UIAutomationStrategy(InteractionStrategy):
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        return (True, f"Executed '{goal.intent.value}' via UI Automation", {"method": InteractionMethod.UI_AUTOMATION.value})


class BrowserDOMStrategy(InteractionStrategy):
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        return (True, f"Executed '{goal.intent.value}' via Browser DOM", {"method": InteractionMethod.BROWSER_DOM.value})


class KeyboardStrategy(InteractionStrategy):
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        return (True, f"Executed '{goal.intent.value}' via Keyboard", {"method": InteractionMethod.KEYBOARD.value})


class MouseStrategy(InteractionStrategy):
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        return (True, f"Executed '{goal.intent.value}' via Mouse", {"method": InteractionMethod.MOUSE.value})


class VisionStrategy(InteractionStrategy):
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        return (True, f"Executed '{goal.intent.value}' via Screen Vision", {"method": InteractionMethod.VISION.value})
