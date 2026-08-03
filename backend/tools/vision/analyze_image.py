import logging
import time
from typing import Any, Dict
from tools.base import Tool
from tools.result import ToolResult
from vision.manager import VisionManager

logger = logging.getLogger("AURA.Tools.Vision.AnalyzeImage")


class AnalyzeImageTool(Tool):
    """Tool for performing multimodal scene analysis on an image."""

    def __init__(self, vision_mgr: VisionManager = None):
        self.vision_mgr = vision_mgr if vision_mgr is not None else VisionManager()

    @property
    def name(self) -> str:
        return "analyze_image"

    @property
    def description(self) -> str:
        return "Analyzes an image file, screenshot, or URL using Multimodal Vision AI."

    @property
    def category(self) -> str:
        return "vision"

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        start_time = time.time()
        image_path = parameters.get("image_path") or parameters.get("source") or parameters.get("filepath")
        prompt = parameters.get("prompt", "Describe this image in detail.")

        if not image_path:
            return ToolResult(
                success=False,
                message="No image path or source provided.",
                execution_time=time.time() - start_time
            )

        try:
            res = self.vision_mgr.analyze_image(image_path, prompt=prompt)
            elapsed = time.time() - start_time
            return ToolResult(
                success=True,
                message=res.description,
                data=res.to_dict(),
                execution_time=elapsed
            )
        except Exception as e:
            logger.error(f"AnalyzeImageTool execution failed: {e}")
            return ToolResult(
                success=False,
                message=f"Failed to analyze image: {e}",
                execution_time=time.time() - start_time
            )
