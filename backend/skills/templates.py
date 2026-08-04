from typing import List
from skills.models import CognitiveSkill, SkillCategory, SkillInput, SkillOutput


def get_builtin_skills() -> List[CognitiveSkill]:
    """Generate default built-in Cognitive Skills."""
    dev_skill = CognitiveSkill(
        skill_id="skill_developer",
        name="Developer Skill",
        description="Full-stack software project creation, dependency installation, and code analysis.",
        goal_template="Create and configure project '{project_name}' using tech stack '{tech_stack}'",
        category=SkillCategory.DEVELOPMENT,
        required_tools=["open_project", "run_terminal_command", "run_tests"],
        tags=["coding", "software", "development"]
    )

    research_skill = CognitiveSkill(
        skill_id="skill_research",
        name="Research Assistant",
        description="Conduct deep web research, summarize knowledge notes, and format citations.",
        goal_template="Research topic '{topic}' and generate a comparative summary report.",
        category=SkillCategory.RESEARCH,
        required_tools=["open_page", "search_knowledge"],
        tags=["research", "analysis", "study"]
    )

    writer_skill = CognitiveSkill(
        skill_id="skill_content_writer",
        name="Content Writer",
        description="Draft blog posts, technical articles, and documentation.",
        goal_template="Write documentation for '{topic}' in tone '{tone}'",
        category=SkillCategory.WRITING,
        required_tools=["generate_readme"],
        tags=["writing", "content", "markdown"]
    )

    teacher_skill = CognitiveSkill(
        skill_id="skill_teacher",
        name="Teacher Skill",
        description="Explain complex technical or academic topics with examples and quizzes.",
        goal_template="Explain topic '{concept}' for audience level '{level}'",
        category=SkillCategory.TEACHING,
        required_tools=["search_knowledge"],
        tags=["learning", "teaching", "education"]
    )

    pm_skill = CognitiveSkill(
        skill_id="skill_product_manager",
        name="Product Manager",
        description="Draft product briefs, user stories, and acceptance criteria.",
        goal_template="Create product requirements document for '{feature}'",
        category=SkillCategory.PRODUCTIVITY,
        required_tools=["chat"],
        tags=["product", "management", "planning"]
    )

    return [dev_skill, research_skill, writer_skill, teacher_skill, pm_skill]
