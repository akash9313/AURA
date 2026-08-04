import logging
from typing import Any, Dict, Optional
from browser.manager.configuration import BrowserManagerConfig

logger = logging.getLogger("AURA.Browser.Manager.Factory")


class BrowserFactory:
    """
    Factory Pattern Implementation for Playwright Browser Engines.
    Launches Chromium, Firefox, or WebKit instances based on configuration parameters.
    """

    def __init__(self, config: Optional[BrowserManagerConfig] = None):
        self.config = config or BrowserManagerConfig()

    async def launch_browser(self, playwright_instance: Any) -> Any:
        browser_type_name = self.config.browser_type.lower()
        logger.info(f"Factory launching browser '{browser_type_name.upper()}' (Headless={self.config.headless})...")

        launch_options: Dict[str, Any] = {
            "headless": self.config.headless,
        }

        if self.config.executable_path:
            launch_options["executable_path"] = self.config.executable_path

        if browser_type_name == "firefox":
            browser_launcher = playwright_instance.firefox
        elif browser_type_name == "webkit":
            browser_launcher = playwright_instance.webkit
        else:
            browser_launcher = playwright_instance.chromium

        browser = await browser_launcher.launch(**launch_options)
        logger.info(f"Browser '{browser_type_name.upper()}' launched successfully via Factory.")
        return browser
