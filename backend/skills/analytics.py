import logging
from typing import Dict
from skills.models import CognitiveSkill

logger = logging.getLogger("AURA.Skills.Analytics")


class SkillAnalyticsRecorder:
    """Tracks skill performance metrics: execution count, success rate, and popularity."""

    def record_execution(self, skill: CognitiveSkill, duration_ms: float, success: bool) -> None:
        skill.metrics.execution_count += 1
        if success:
            skill.metrics.success_count += 1
        else:
            skill.metrics.failure_count += 1

        skill.metrics.popularity_score = float(skill.metrics.execution_count)
        logger.info(f"Recorded skill metric for '{skill.name}': Total={skill.metrics.execution_count}, Success={skill.metrics.success_count}")
