import logging
import time
from typing import Any, Dict, List, Optional
from learning.models import UserPreference

logger = logging.getLogger("AURA.Learning.Preferences")


class PreferenceEngine:
    """
    Manages user preferences with explicit/inferred tracking and full privacy controls.
    """

    DEFAULT_PREFERENCES = {
        "preferred_browser": "chrome",
        "preferred_editor": "vscode",
        "preferred_terminal": "powershell",
        "preferred_shell": "cmd",
        "preferred_coding_language": "python",
        "preferred_response_length": "concise",
        "preferred_tone": "professional",
        "preferred_automation_style": "safe",
    }

    def __init__(self):
        self.preferences: Dict[str, UserPreference] = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        for key, val in self.DEFAULT_PREFERENCES.items():
            self.preferences[key] = UserPreference(key=key, value=val, confidence_score=1.0, source="explicit")

    def get_preference(self, key: str) -> Optional[UserPreference]:
        return self.preferences.get(key)

    def set_preference(self, key: str, value: Any, source: str = "explicit", confidence: float = 1.0) -> UserPreference:
        pref = UserPreference(key=key, value=value, confidence_score=confidence, source=source, updated_at=time.time())
        self.preferences[key] = pref
        logger.info(f"User preference updated: '{key}' = '{value}' [{source}]")
        return pref

    def infer_preference_from_action(self, action_type: str, item_name: str) -> None:
        """Infer user preference from repeated application or tool usage."""
        item_lower = item_name.lower()
        if "chrome" in item_lower:
            self.set_preference("preferred_browser", "chrome", source="inferred", confidence=0.85)
        elif "edge" in item_lower:
            self.set_preference("preferred_browser", "edge", source="inferred", confidence=0.85)
        elif "code" in item_lower or "vscode" in item_lower:
            self.set_preference("preferred_editor", "vscode", source="inferred", confidence=0.90)

    def export_preferences(self) -> Dict[str, Any]:
        """Privacy API: Export all learned preferences."""
        return {key: pref.to_dict() for key, pref in self.preferences.items()}

    def clear_learned_preferences(self) -> None:
        """Privacy API: Clear all inferred preferences."""
        self.preferences.clear()
        self._initialize_defaults()
        logger.info("Cleared all inferred preferences.")
