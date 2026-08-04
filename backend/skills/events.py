from enum import Enum


class SkillEvent(Enum):
    """Event definitions for Cognitive Skills Engine."""
    SKILL_REGISTERED = "skill_registered"
    SKILL_EXECUTED = "skill_executed"
    SKILL_COMPLETED = "skill_completed"
    SKILL_FAILED = "skill_failed"
    SKILL_UPDATED = "skill_updated"
