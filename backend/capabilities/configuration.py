"""
Capability Registry Configuration.
Configures experimental capabilities, deprecation handling, and platform restrictions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CapabilityConfig:
    """Configuration parameters for Capability Registry Subsystem."""
    enable_experimental: bool = False
    allow_deprecated_fallback: bool = True
    platform_filter: Optional[str] = "windows"
