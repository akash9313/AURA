import logging
import time
from typing import Any, Dict, Optional
from skills.analytics import SkillAnalyticsRecorder
from skills.models import CognitiveSkill, CompositeSkill
from skills.permissions import SkillPermissionValidator
from skills.registry import SkillRegistry
from skills.validator import SkillValidator
from workflow.engine import WorkflowEngine

logger = logging.getLogger("AURA.Skills.Executor")


class SkillExecutor:
    """
    Executes atomic and composite Cognitive Skills by orchestrating WorkflowEngine mission runs.
    """

    def __init__(
        self,
        registry: SkillRegistry,
        workflow_engine: Optional[WorkflowEngine] = None
    ):
        self.registry = registry
        self.workflow_engine = workflow_engine if workflow_engine is not None else WorkflowEngine()
        self.validator = SkillValidator()
        self.permissions = SkillPermissionValidator()
        self.analytics = SkillAnalyticsRecorder()

    def execute_skill(self, skill_id: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            raise KeyError(f"Skill '{skill_id}' not found in registry.")

        t0 = time.time()
        self.validator.validate_skill(skill)
        self.permissions.can_execute(skill)

        # Build natural goal from template
        inputs = inputs or {}
        try:
            goal = skill.goal_template.format(**inputs)
        except KeyError:
            goal = skill.goal_template

        logger.info(f"Executing Skill '{skill.name}' with goal: '{goal}'")
        report = self.workflow_engine.run_mission(goal)

        dt = (time.time() - t0) * 1000.0
        success = (report.get("status") == "completed")
        self.analytics.record_execution(skill, dt, success)

        return {
            "skill_id": skill_id,
            "skill_name": skill.name,
            "goal": goal,
            "workflow_report": report,
            "execution_time_ms": dt
        }

    def execute_composite(self, composite_skill: CompositeSkill, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"🚀 Executing Composite Skill '{composite_skill.name}' ({len(composite_skill.child_skill_ids)} stages)")
        results = []

        for sid in composite_skill.child_skill_ids:
            res = self.execute_skill(sid, inputs=inputs)
            results.append(res)

        return {
            "composite_id": composite_skill.composite_id,
            "composite_name": composite_skill.name,
            "stage_results": results
        }
