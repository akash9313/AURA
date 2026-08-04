"""
AURA UI Automation Engine.
Provides semantic desktop application understanding and control via Microsoft UI Automation abstractions.
"""

from computer.uia.actions import UIElementActionExecutor
from computer.uia.automation_provider import MicrosoftUIAutomationProvider
from computer.uia.automation_tree import AURAUIElementNode, UIAutomationTree, UIElementVisitor
from computer.uia.cache import UIElementCache
from computer.uia.configuration import UIAutomationConfig
from computer.uia.events import UIAutomationEvent
from computer.uia.locator import UIElementLocator
from computer.uia.models import (
    AURAUIElement,
    ControlType,
    UIActionResult,
    UIElementQuery,
    UIPattern,
)
from computer.uia.service import UIAutomationService
from computer.uia.verifier import UIElementVerifier

__all__ = [
    "UIAutomationService",
    "MicrosoftUIAutomationProvider",
    "UIAutomationTree",
    "AURAUIElementNode",
    "UIElementVisitor",
    "UIElementLocator",
    "UIElementActionExecutor",
    "UIElementVerifier",
    "UIElementCache",
    "UIAutomationConfig",
    "AURAUIElement",
    "ControlType",
    "UIPattern",
    "UIElementQuery",
    "UIActionResult",
    "UIAutomationEvent",
]
