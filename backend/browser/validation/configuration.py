"""
Browser Capability Validation Configuration.
Configures test URLs, timeouts, recovery retries, and verification parameters.
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class BrowserValidationConfig:
    """Configuration parameters for Browser Capability Validation."""
    timeout_sec: float = 30.0
    max_retries: int = 3
    headless: bool = True
    screenshot_on_verify: bool = True
    target_urls: Dict[str, str] = field(default_factory=lambda: {
        "example": "https://example.com",
        "search": "https://www.google.com",
        "form": "https://httpbin.org/forms/post",
        "download": "https://httpbin.org/bytes/1024",
    })
