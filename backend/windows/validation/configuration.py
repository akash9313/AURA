"""
Desktop Capability Validation Configuration.
Configures timeouts, recovery retries, vision fallback, and alternative locator options.
"""

from dataclasses import dataclass


@dataclass
class DesktopValidationConfig:
    """Configuration parameters for Desktop Capability Validation."""
    timeout_sec: float = 30.0
    max_retries: int = 3
    backoff_sec: float = 0.5
    enable_vision_fallback: bool = True
    enable_alternative_locator: bool = True
    screenshot_on_verify: bool = True
