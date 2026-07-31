from abc import ABC, abstractmethod
from typing import Dict, Any
from tools.result import ToolResult


class Tool(ABC):
    """
    Abstract base class for all tools in the AURA AI Operating System.
    
    Every concrete tool implementation must define:
    - name: Unique identifier for the tool.
    - description: Clear summary of the tool's capabilities.
    - category: The functional group (e.g. 'windows', 'filesystem', 'browser', 'chat').
    - execute(parameters): Action execution logic returning a standardized ToolResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier string for the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category domain of the tool (e.g. 'windows', 'filesystem', 'browser')."""
        pass

    @abstractmethod
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            parameters (dict): Arguments required by the tool.

        Returns:
            ToolResult: Standardized result object containing status, message, and data.
        """
        pass