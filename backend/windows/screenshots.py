import logging
import os
import time
from typing import Dict, Optional
from vision.screenshot import ScreenshotManager
from windows.models import AutomationResult

logger = logging.getLogger("AURA.Windows.Screenshots")


class WindowsScreenshotManager:
    """
    Manager responsible for screen capture across full desktop screens, active windows, or region bounding boxes.
    """

    def __init__(self):
        self._shot_mgr = ScreenshotManager()

    def capture_screen(self, output_path: str = "screenshot.png") -> AutomationResult:
        """Capture full screen image and save to disk."""
        start_time = time.time()
        try:
            path = self._shot_mgr.capture_screen(output_path)
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message=f"Screenshot saved to '{path}'",
                data={"filepath": path},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(
                success=False,
                message=f"Screenshot capture failed: {e}",
                execution_time=elapsed
            )

    def capture_region(self, region: Dict[str, int], output_path: str = "region.png") -> AutomationResult:
        """Capture specific screen bounding region (x, y, width, height)."""
        start_time = time.time()
        try:
            path = self._shot_mgr.capture_region(region, output_path)
            elapsed = time.time() - start_time
            return AutomationResult(
                success=True,
                message=f"Region screenshot saved to '{path}'",
                data={"filepath": path, "region": region},
                execution_time=elapsed
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return AutomationResult(
                success=False,
                message=f"Region screenshot capture failed: {e}",
                execution_time=elapsed
            )
