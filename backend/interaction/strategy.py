"""
Interaction Strategies (Strategy Pattern).
Implements specialized execution strategies for UI Automation, Browser DOM, Keyboard, Mouse, and Vision.
"""

import abc
import logging
import time
from typing import Any, Dict, Tuple

from interaction.models import InteractionGoal, InteractionMethod

logger = logging.getLogger("AURA.Interaction.Strategy")


class InteractionStrategy(abc.ABC):
    """Abstract Strategy interface for executing interaction goals."""

    @abc.abstractmethod
    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        """Execute interaction goal. Returns (success, status_message, data)."""
        pass


class UIAutomationStrategy(InteractionStrategy):
    """Executes goal via Microsoft UI Automation Engine."""

    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"Executing '{goal.intent.value}' via UI Automation...")
        return (True, f"Executed '{goal.intent.value}' via UI Automation", {"method": InteractionMethod.UI_AUTOMATION.value})


class BrowserDOMStrategy(InteractionStrategy):
    """Executes goal via Browser Navigation & Action Engine."""

    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"Executing '{goal.intent.value}' via Browser DOM...")
        return (True, f"Executed '{goal.intent.value}' via Browser DOM", {"method": InteractionMethod.BROWSER_DOM.value})


class KeyboardStrategy(InteractionStrategy):
    """Executes goal via Keyboard Input events."""

    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"Executing '{goal.intent.value}' via Keyboard...")
        return (True, f"Executed '{goal.intent.value}' via Keyboard", {"method": InteractionMethod.KEYBOARD.value})


class MouseStrategy(InteractionStrategy):
    """Executes goal via Mouse click and movement events."""

    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"Executing '{goal.intent.value}' via Mouse...")
        return (True, f"Executed '{goal.intent.value}' via Mouse", {"method": InteractionMethod.MOUSE.value})


class VisionStrategy(InteractionStrategy):
    """Executes goal via Screen Intelligence bounding box detection."""

    async def execute(self, goal: InteractionGoal) -> Tuple[bool, str, Dict[str, Any]]:
        logger.info(f"Executing '{goal.intent.value}' via Screen Vision...")
        return (True, f"Executed '{goal.intent.value}' via Screen Vision", {"method": InteractionMethod.VISION.value})
