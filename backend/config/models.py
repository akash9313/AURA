from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FeatureFlagState:
    name: str
    enabled: bool
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
        }


@dataclass
class CategoryConfig:
    name: str
    settings: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)


@dataclass
class AppConfig:
    environment: str = "development"
    debug: bool = True
    categories: Dict[str, CategoryConfig] = field(default_factory=dict)
    feature_flags: Dict[str, FeatureFlagState] = field(default_factory=dict)

    def get(self, category: str, key: str, default: Any = None) -> Any:
        cat = self.categories.get(category)
        if cat:
            return cat.get(key, default)
        return default

    def is_feature_enabled(self, feature_name: str) -> bool:
        flag = self.feature_flags.get(feature_name)
        return flag.enabled if flag else False
