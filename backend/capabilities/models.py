"""
Capability Registry Domain Models.
Defines CapabilityCategory, Capability, and CapabilityMatchResult.
Single source of truth describing everything AURA can execute.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CapabilityCategory(Enum):
    """Categories of AURA capabilities."""
    APPLICATION = "application"
    BROWSER = "browser"
    FILESYSTEM = "filesystem"
    DOCUMENT = "document"
    TERMINAL = "terminal"
    COMMUNICATION = "communication"
    SYSTEM = "system"
    REASONING = "reasoning"


@dataclass
class Capability:
    """Production capability model describing an executable function."""
    capability_id: str
    name: str
    description: str
    category: CapabilityCategory
    version: str = "1.0.0"
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    supported_platforms: List[str] = field(default_factory=lambda: ["windows", "linux", "darwin"])
    dependencies: List[str] = field(default_factory=list)
    confidence: float = 0.95
    estimated_duration: float = 1.0
    is_deprecated: bool = False
    replaced_by: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    is_experimental: bool = False
    enabled: bool = True
    priority: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "required_permissions": self.required_permissions,
            "supported_platforms": self.supported_platforms,
            "dependencies": self.dependencies,
            "confidence": self.confidence,
            "estimated_duration": self.estimated_duration,
            "is_deprecated": self.is_deprecated,
            "replaced_by": self.replaced_by,
            "aliases": self.aliases,
            "is_experimental": self.is_experimental,
            "enabled": self.enabled,
            "priority": self.priority,
        }


@dataclass
class CapabilityMatchResult:
    """Result of matching a planner request against available capabilities."""
    capability: Capability
    confidence_score: float
    match_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability.capability_id,
            "capability_name": self.capability.name,
            "confidence_score": self.confidence_score,
            "match_reason": self.match_reason,
        }
