from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class BrowserManagerConfig:
    """Configurable infrastructure settings for Playwright Browser Manager."""
    browser_type: str = "chromium"  # chromium, firefox, webkit
    headless: bool = True
    executable_path: Optional[str] = None
    user_data_dir: Optional[str] = None
    download_directory: Optional[str] = None
    viewport_width: int = 1280
    viewport_height: int = 800
    locale: str = "en-US"
    timezone_id: str = "America/New_York"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AURA-BrowserEngine/1.0"
    proxy: Optional[Dict[str, str]] = None
    navigation_timeout_ms: float = 30000.0
    command_timeout_ms: float = 30000.0
    auto_restart_on_crash: bool = True
    max_crash_retries: int = 3
