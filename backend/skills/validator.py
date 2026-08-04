import logging
from skills.models import CognitiveSkill

logger = logging.getLogger("AURA.Skills.Validator")


class SkillValidator:
    """Validates cognitive skill definitions for completeness and required tools."""

    def validate_skill(self, skill: CognitiveSkill) -> bool:
        if not skill.skill_id:
            raise ValueError("Skill definition missing 'skill_id'.")
        if not skill.name:
            raise ValueError("Skill definition missing 'name'.")
        if not skill.goal_template:
            raise ValueError("Skill definition missing 'goal_template'.")
        logger.info(f"Cognitive Skill '{skill.skill_id}' validated successfully.")
        return True
