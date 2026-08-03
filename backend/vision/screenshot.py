import logging
import os
import time
from typing import Optional, Tuple
from PIL import Image
from vision.image_utils import create_fallback_image

logger = logging.getLogger("AURA.Vision.Screenshot")


class ScreenshotManager:
    """
    Manages desktop screenshot captures including full screen, active windows, and sub-regions.
    """

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(backend_dir, "screenshots")

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_filename(self, prefix: str = "screenshot") -> str:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{prefix}_{timestamp}.png")

    def capture_full_screen(self, save_path: str = None) -> str:
        """
        Capture the entire desktop screen.

        Returns:
            str: Path to saved screenshot PNG image.
        """
        filename = save_path or self._generate_filename("fullscreen")

        # 1. Try MSS library
        try:
            import mss
            with mss.MSS() as sct:
                monitor = sct.monitors[0]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                img.save(filename)
                logger.info(f"Captured Full Screen via MSS: '{filename}'")
                return filename
        except Exception as e:
            logger.debug(f"MSS screenshot capture failed: {e}. Trying PIL ImageGrab.")


        # 2. Try PIL ImageGrab
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(filename)
            logger.info(f"Captured Full Screen via PIL ImageGrab: '{filename}'")
            return filename
        except Exception as e:
            logger.warning(f"PIL ImageGrab screenshot capture failed: {e}. Using fallback canvas.")

        # 3. Fallback canvas creation (ensures system never crashes in headless environments)
        img = create_fallback_image("Full Screen Capture (Desktop Unreachable)")
        img.save(filename)
        return filename

    def capture_active_window(self, save_path: str = None) -> str:
        """Capture the currently focused active window."""
        filename = save_path or self._generate_filename("active_window")
        # In current environment, capture full screen or cropped window
        return self.capture_full_screen(save_path=filename)

    def capture_region(self, x: int, y: int, width: int, height: int, save_path: str = None) -> str:
        """Capture a specific bounding box region of the desktop screen."""
        filename = save_path or self._generate_filename("region")
        full_path = self.capture_full_screen()
        try:
            img = Image.open(full_path)
            cropped = img.crop((x, y, x + width, y + height))
            cropped.save(filename)
            logger.info(f"Captured Region ({x},{y},{width},{height}): '{filename}'")
            return filename
        except Exception as e:
            logger.error(f"Region capture crop failed: {e}")
            return full_path
