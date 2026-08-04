from dataclasses import dataclass


@dataclass
class BrowserConfig:
    """Configurable settings for Playwright Browser Automation Service."""
    provider_name: str = "playwright"
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    default_timeout_ms: float = 30000.0
    viewport_width: int = 1280
    viewport_height: int = 800
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AURA-BrowserAgent/1.0"
