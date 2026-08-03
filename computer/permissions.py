import logging
from computer.models import ActionType, SafetyLevel
from computer.safety import SafetySystem

logger = logging.getLogger("AURA.Computer.Permissions")


class ComputerPermissions:
    """
    Permission validator ensuring desktop actions strictly comply with AURA OS security policies.
    """

    def __init__(self, safety_system: SafetySystem):
        self.safety_system = safety_system

    def validate_permission(self, action: ActionType, details: str = "") -> bool:
        """Validate whether an action is permitted under current policy."""
        safety_level, is_allowed = self.safety_system.evaluate_action(action, details)
        if not is_allowed:
            logger.warning(f"Action '{action.value}' blocked by security policy.")
            return False
        return True
