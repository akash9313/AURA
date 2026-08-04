import unittest
from skills.analytics import SkillAnalyticsRecorder
from skills.composer import SkillComposer
from skills.executor import SkillExecutor
from skills.marketplace import SkillMarketplace
from skills.models import CognitiveSkill, SkillCategory
from skills.permissions import SkillPermissionValidator
from skills.registry import SkillRegistry
from skills.validator import SkillValidator


class TestCognitiveSkillsEngine(unittest.TestCase):

    def setUp(self):
        self.registry = SkillRegistry()
        self.validator = SkillValidator()
        self.permissions = SkillPermissionValidator()
        self.composer = SkillComposer(self.registry)
        self.marketplace = SkillMarketplace(self.registry)
        self.executor = SkillExecutor(self.registry)

    def test_builtin_skills_registration(self):
        """Test default built-in skill loading."""
        skills = self.registry.list_skills()
        self.assertGreaterEqual(len(skills), 5)
        dev_skill = self.registry.get_skill("skill_developer")
        self.assertIsNotNone(dev_skill)
        self.assertEqual(dev_skill.category, SkillCategory.DEVELOPMENT)

    def test_custom_skill_registration_and_validation(self):
        """Test registering and validating custom skills."""
        custom_skill = CognitiveSkill(
            skill_id="skill_fin_analysis",
            name="Financial Analyst",
            description="Analyze revenue growth and profitability.",
            goal_template="Analyze financial statements for company '{company}'",
            category=SkillCategory.ANALYTICS
        )
        self.registry.register_skill(custom_skill)
        self.assertTrue(self.validator.validate_skill(custom_skill))
        self.assertTrue(self.permissions.can_execute(custom_skill))

    def test_skill_composer(self):
        """Test composing multiple atomic skills into a CompositeSkill."""
        comp = self.composer.compose(
            name="Deep Product Research Pipeline",
            description="Run research followed by content writing.",
            skill_ids=["skill_research", "skill_content_writer"]
        )
        self.assertEqual(len(comp.child_skill_ids), 2)
        self.assertTrue(comp.composite_id.startswith("comp_"))

    def test_skill_marketplace_search(self):
        """Test searching skills by query and category."""
        matched = self.marketplace.search_skills("Research", category=SkillCategory.RESEARCH)
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].skill_id, "skill_research")

    def test_skill_execution(self):
        """Test atomic and composite skill execution."""
        # 1. Atomic Skill
        res_atomic = self.executor.execute_skill("skill_developer", inputs={"project_name": "AURA OS", "tech_stack": "Python"})
        self.assertEqual(res_atomic["skill_id"], "skill_developer")

        # 2. Composite Skill
        comp = self.composer.compose(
            name="Full Pipeline",
            description="Research -> Write",
            skill_ids=["skill_research", "skill_content_writer"]
        )
        res_comp = self.executor.execute_composite(comp)
        self.assertEqual(len(res_comp["stage_results"]), 2)


if __name__ == "__main__":
    unittest.main()
