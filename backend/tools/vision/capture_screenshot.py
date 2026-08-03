import logging
import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from vision.manager import VisionManager

logger = logging.getLogger("AURA.Tools.Vision.CaptureScreenshot")


class CaptureScreenshotTool(Tool):
    """Tool for taking and saving a desktop screenshot."""

    def __init__(self, vision_mgr: VisionManager = None):
        self.vision_mgr = vision_mgr if vision_mgr is not None else VisionManager()

    @property
    def name(self) -> str:
        return "capture_screenshot"

    @property
    def description(self) -> str:
        return "Captures a desktop screenshot and saves it as an image file."

    @property
    def category(self) -> str:
        return "vision"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        try:
            path = self.vision_mgr.capture_screen()
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=f"Screenshot captured and saved to '{path}'.",
                data={"filepath": path},
                execution_time=elapsed
            )
        except Exception as e:
            logger.error(f"CaptureScreenshotTool failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to capture screenshot: {e}",
                execution_time=time.time() - start_time
            )
