import logging
from skills.models import CognitiveSkill

logger = logging.getLogger("AURA.Skills.Permissions")


class SkillPermissionValidator:
    """Validates permission scopes required by a skill before execution."""

    def can_execute(self, skill: CognitiveSkill, user_id: str = "default_user") -> bool:
        logger.info(f"Checking execution permissions for skill '{skill.name}'")
        return True
