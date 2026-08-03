import logging
import os
import time
from typing import Optional
from PIL import Image
from vision.image_utils import create_fallback_image

logger = logging.getLogger("AURA.Vision.Camera")


class CameraManager:
    """
    Manages camera device capture for AURA.
    """

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(backend_dir, "camera_captures")

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_filename(self) -> str:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"camera_{timestamp}.png")

    def capture_image(self, device_id: int = 0, save_path: str = None) -> str:
        """
        Capture a frame from the specified camera device.

        Args:
            device_id (int): Camera device index (default 0).
            save_path (str, optional): Target file path to save image.

        Returns:
            str: Absolute file path to captured image.
        """
        filename = save_path or self._generate_filename()

        try:
            import cv2
            cap = cv2.VideoCapture(device_id, cv2.CAP_DSHOW)
            if cap.isOpened():
                # Read a frame
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None and frame.size > 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img.save(filename)
                    logger.info(f"Captured camera frame via OpenCV: '{filename}'")
                    return filename
        except Exception as e:
            logger.debug(f"OpenCV camera capture failed ({e}). Using camera fallback canvas.")

        # Fallback synthetic canvas if no hardware camera is present or accessible
        img = create_fallback_image("Camera Capture (Hardware Camera Unreachable)")
        img.save(filename)
        logger.info(f"Saved fallback camera image: '{filename}'")
        return filename
