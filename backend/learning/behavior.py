import logging
from typing import Any, Dict
from learning.preferences import PreferenceEngine

logger = logging.getLogger("AURA.Learning.Behavior")


class BehaviorAdapter:
    """
    Adapts agent decision policies dynamically based on active learned user preferences.
    """

    def __init__(self, preference_engine: PreferenceEngine):
        self.preference_engine = preference_engine

    def apply_behavioral_overrides(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned user preferences to action or tool parameters."""
        updated = dict(params)
        browser_pref = self.preference_engine.get_preference("preferred_browser")
        if browser_pref and "browser" in params and params["browser"] == "default":
            updated["browser"] = browser_pref.value

        editor_pref = self.preference_engine.get_preference("preferred_editor")
        if editor_pref and "editor" in params and params["editor"] == "default":
            updated["editor"] = editor_pref.value

        return updated
