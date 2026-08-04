from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class SkillCategory(Enum):
    DEVELOPMENT = "development"
    RESEARCH = "research"
    WRITING = "writing"
    TEACHING = "teaching"
    PRESENTATION = "presentation"
    ANALYTICS = "analytics"
    PRODUCTIVITY = "productivity"
    DESIGN = "design"
    BUSINESS = "business"
    CUSTOM = "custom"


@dataclass
class SkillInput:
    name: str
    description: str
    required: bool = True
    default_value: Optional[Any] = None


@dataclass
class SkillOutput:
    name: str
    description: str
    data_type: str = "string"


@dataclass
class SkillMetric:
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time_ms: float = 0.0
    popularity_score: float = 0.0


@dataclass
class CognitiveSkill:
    """Represents a high-level, reusable cognitive capability in AURA."""
    skill_id: str
    name: str
    description: str
    goal_template: str
    category: SkillCategory
    required_tools: List[str] = field(default_factory=list)
    required_plugins: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    inputs: List[SkillInput] = field(default_factory=list)
    outputs: List[SkillOutput] = field(default_factory=list)
    estimated_time_seconds: float = 60.0
    confidence_score: float = 0.9
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metrics: SkillMetric = field(default_factory=SkillMetric)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "goal_template": self.goal_template,
            "category": self.category.value,
            "required_tools": self.required_tools,
            "required_plugins": self.required_plugins,
            "permissions": self.permissions,
            "estimated_time_seconds": self.estimated_time_seconds,
            "confidence_score": self.confidence_score,
            "version": self.version,
            "tags": self.tags,
        }


@dataclass
class CompositeSkill:
    """A higher-level skill composed from a sequence of child skills."""
    composite_id: str
    name: str
    description: str
    child_skill_ids: List[str]
    created_at: float = field(default_factory=time.time)
