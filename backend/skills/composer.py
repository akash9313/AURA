import logging
import uuid
from typing import Dict, List, Optional
from skills.models import CompositeSkill
from skills.registry import SkillRegistry

logger = logging.getLogger("AURA.Skills.Composer")


class SkillComposer:
    """
    Composes complex multi-skill pipelines (e.g. Research -> Writing -> Presentation -> Email).
    """

    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.composite_skills: Dict[str, CompositeSkill] = {}

    def compose(self, name: str, description: str, skill_ids: List[str]) -> CompositeSkill:
        for sid in skill_ids:
            if not self.registry.get_skill(sid):
                raise KeyError(f"Child skill '{sid}' not found in registry.")

        cid = f"comp_{uuid.uuid4().hex[:8]}"
        comp = CompositeSkill(composite_id=cid, name=name, description=description, child_skill_ids=skill_ids)
        self.composite_skills[cid] = comp

        logger.info(f"Composed composite skill '{name}' (ID: {cid}) with {len(skill_ids)} child skill(s).")
        return comp
