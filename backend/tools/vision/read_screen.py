import logging
import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from vision.manager import VisionManager

logger = logging.getLogger("AURA.Tools.Vision.ReadScreen")


class ReadScreenTool(Tool):
    """Tool for capturing the current screen and reading UI elements / text."""

    def __init__(self, vision_mgr: VisionManager = None):
        self.vision_mgr = vision_mgr if vision_mgr is not None else VisionManager()

    @property
    def name(self) -> str:
        return "read_screen"

    @property
    def description(self) -> str:
        return "Captures the active desktop screen, reads visible text, and detects UI elements."

    @property
    def category(self) -> str:
        return "vision"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        try:
            screenshot_path = self.vision_mgr.capture_screen()
            result = self.vision_mgr.analyze_image(screenshot_path, prompt="Describe what is currently visible on the screen.")
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=result.description,
                data={"screenshot_path": screenshot_path, "vision_result": result.to_dict()},
                execution_time=elapsed
            )
        except Exception as e:
            logger.error(f"ReadScreenTool execution failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to read screen: {e}",
                execution_time=time.time() - start_time
            )
