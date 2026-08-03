import logging
import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from vision.manager import VisionManager

logger = logging.getLogger("AURA.Tools.Vision.CameraCapture")


class CameraCaptureTool(Tool):
    """Tool for taking a camera image photo."""

    def __init__(self, vision_mgr: VisionManager = None):
        self.vision_mgr = vision_mgr if vision_mgr is not None else VisionManager()

    @property
    def name(self) -> str:
        return "camera_capture"

    @property
    def description(self) -> str:
        return "Captures a photo frame from the webcam/camera."

    @property
    def category(self) -> str:
        return "vision"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        device_id = parameters.get("device_id", 0)
        try:
            path = self.vision_mgr.capture_camera(device_id=device_id)
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=f"Camera photo captured and saved to '{path}'.",
                data={"filepath": path},
                execution_time=elapsed
            )
        except Exception as e:
            logger.error(f"CameraCaptureTool failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to capture camera photo: {e}",
                execution_time=time.time() - start_time
            )
