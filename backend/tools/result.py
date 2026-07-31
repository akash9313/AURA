from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """
    Standardized result data structure returned by all AURA tools upon execution.

    Attributes:
        success (bool): Whether the tool execution completed successfully.
        message (str): Human-readable status message or response description.
        data (Optional[Any]): Optional structured data payload produced by the tool.
        execution_time (float): Time taken to execute the tool in seconds.
    """
    success: bool
    message: str
    data: Optional[Any] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert ToolResult into a dictionary representation."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "execution_time": self.execution_time
        }

    def __getitem__(self, key: str) -> Any:
        """Allow subscript access (e.g. result['success']) for dictionary compatibility."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"ToolResult has no attribute '{key}'")

    def get(self, key: str, default: Any = None) -> Any:
        """Allow dictionary-like get access."""
        return getattr(self, key, default)

    def __eq__(self, other: Any) -> bool:
        """Support equality comparison with another ToolResult or dict."""
        if isinstance(other, dict):
            # Check basic fields success and message for dict comparison
            if "success" in other and "message" in other:
                return self.success == other["success"] and self.message == other["message"]
            return self.to_dict() == other
        if isinstance(other, ToolResult):
            return (
                self.success == other.success and
                self.message == other.message and
                self.data == other.data
            )
        return False
