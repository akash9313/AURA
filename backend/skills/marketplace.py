import logging
from typing import List, Optional
from skills.models import CognitiveSkill, SkillCategory
from skills.registry import SkillRegistry

logger = logging.getLogger("AURA.Skills.Marketplace")


class SkillMarketplace:
    """
    Skill discovery engine supporting search, tag filtering, category filtering, and recommendations.
    """

    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def search_skills(self, query: str, category: Optional[SkillCategory] = None) -> List[CognitiveSkill]:
        query_lower = query.lower()
        matched = []

        for skill in self.registry.list_skills():
            if category and skill.category != category:
                continue

            if query_lower in skill.name.lower() or query_lower in skill.description.lower() or any(query_lower in t.lower() for t in skill.tags):
                matched.append(skill)

        return matched
