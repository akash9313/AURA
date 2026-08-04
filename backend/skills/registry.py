import logging
from typing import Dict, List, Optional
from skills.models import CognitiveSkill
from skills.templates import get_builtin_skills

logger = logging.getLogger("AURA.Skills.Registry")


class SkillRegistry:
    """Registry tracking built-in and custom Cognitive Skills."""

    def __init__(self):
        self.skills: Dict[str, CognitiveSkill] = {}
        self._load_builtins()

    def _load_builtins(self):
        for s in get_builtin_skills():
            self.register_skill(s)

    def register_skill(self, skill: CognitiveSkill) -> None:
        self.skills[skill.skill_id] = skill
        logger.info(f"Registered Cognitive Skill '{skill.name}' (ID: {skill.skill_id})")

    def get_skill(self, skill_id: str) -> Optional[CognitiveSkill]:
        return self.skills.get(skill_id)

    def list_skills(self) -> List[CognitiveSkill]:
        return list(self.skills.values())

