from dataclasses import dataclass
from typing import Optional


@dataclass
class CapabilityConfig:
    enable_experimental: bool = False
    allow_deprecated_fallback: bool = True
    platform_filter: Optional[str] = "windows"
