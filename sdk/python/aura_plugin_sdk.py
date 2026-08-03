"""
AURA Plugin SDK for Python Developers.
Provides base classes and helper functions for developing AURA plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AuraPlugin(ABC):
    """Abstract base class for Python-based AURA Plugins."""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin resources."""
        pass

    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of tool definitions provided by plugin."""
        pass
