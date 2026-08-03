import logging
from typing import Union
from PIL import Image
from vision.models import VisionResult
from vision.pipeline import VisionPipeline

logger = logging.getLogger("AURA.Vision.Analyzer")


class VisionAnalyzer:
    """
    High-level analyzer for specialized vision tasks (code debugging, chart analysis, document comprehension).
    """

    def __init__(self, pipeline: VisionPipeline = None):
        self.pipeline = pipeline if pipeline is not None else VisionPipeline()

    def analyze_scene(self, image_source: Union[str, bytes, Image.Image], prompt: str = "Describe this scene.") -> VisionResult:
        """Analyze general image scene."""
        return self.pipeline.process(image_source, prompt=prompt)

    def debug_code_screenshot(self, image_source: Union[str, bytes, Image.Image]) -> VisionResult:
        """Analyze a screenshot containing code or terminal error tracebacks."""
        prompt = (
            "This is a screenshot of code or a error traceback.\n"
            "Identify the programming language, locate any syntax or runtime errors, "
            "and explain how to fix the issue."
        )
        return self.pipeline.process(image_source, prompt=prompt, enable_ocr=True, enable_ui=False)

    def analyze_chart_or_graph(self, image_source: Union[str, bytes, Image.Image]) -> VisionResult:
        """Analyze data charts, plots, or diagrams."""
        prompt = (
            "Analyze this chart or diagram.\n"
            "Identify the chart type, axis labels, key trends, data points, and main conclusion."
        )
        return self.pipeline.process(image_source, prompt=prompt, enable_ocr=True, enable_objects=False)
