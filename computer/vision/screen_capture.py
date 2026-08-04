import logging
import time
from typing import Optional, Tuple

from computer.vision.models import ScreenSnapshot
from computer.vision.screenshot_cache import ScreenshotCache

logger = logging.getLogger("AURA.Computer.Vision.ScreenCapture")


class ScreenCaptureEngine:
    def __init__(self, cache: Optional[ScreenshotCache] = None):
        self.cache = cache or ScreenshotCache()

    async def capture_desktop(self) -> ScreenSnapshot:
        start_time = time.time()
        bounds = (0, 0, 1920, 1080)
        snapshot = ScreenSnapshot(
            bounds=bounds,
            scale_factor=1.0,
            timestamp=start_time,
        )

        self.cache.put(snapshot)
        return snapshot

    async def capture_window(self, window_id: str, bounds: Optional[Tuple[int, int, int, int]] = None) -> ScreenSnapshot:
        start_time = time.time()
        win_bounds = bounds or (100, 100, 1024, 768)

        snapshot = ScreenSnapshot(
            bounds=win_bounds,
            scale_factor=1.0,
            timestamp=start_time,
        )

        self.cache.put(snapshot)
        return snapshot

    async def capture_region(self, x: int, y: int, width: int, height: int) -> ScreenSnapshot:
        start_time = time.time()
        bounds = (x, y, width, height)

        snapshot = ScreenSnapshot(
            bounds=bounds,
            scale_factor=1.0,
            timestamp=start_time,
        )

        self.cache.put(snapshot)
        return snapshot
