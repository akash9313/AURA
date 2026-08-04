"""
Screen Intelligence Service.
Top-level AURA service providing visual understanding of the desktop independent of UI Automation APIs.
Integrates frame captures, OCR, object detection, spatial layout analysis, and visual action verification.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from core.service import Service
from computer.vision.events import ScreenVisionEvent
from computer.vision.layout import LayoutNode, ScreenLayoutAnalyzer
from computer.vision.models import (
    OCRResult,
    ScreenSnapshot,
    VisualElement,
    VisualVerificationResult,
)
from computer.vision.screen_capture import ScreenCaptureEngine
from computer.vision.screenshot_cache import ScreenshotCache
from computer.vision.ui_detector import UIDetector

logger = logging.getLogger("AURA.Computer.Vision.Service")


class ScreenIntelligenceService(Service):
    """
    Central service wrapper exposing visual intelligence capabilities to AURA Runtime and Workflow Engine.
    """

    def __init__(
        self,
        bus: Any = None,
    ):
        super().__init__(bus)
        self.cache = ScreenshotCache()
        self.capture_engine = ScreenCaptureEngine(cache=self.cache)
        self.ui_detector = UIDetector()
        self.layout_analyzer = ScreenLayoutAnalyzer()

        logger.info("ScreenIntelligenceService initialized")

    # ------------------------------------------------------------------
    # Captures & Analysis
    # ------------------------------------------------------------------

    async def capture_desktop(self) -> ScreenSnapshot:
        """Capture full primary desktop and publish SCREEN_CAPTURED event."""
        snapshot = await self.capture_engine.capture_desktop()
        self._publish_event(ScreenVisionEvent.SCREEN_CAPTURED, snapshot.to_dict())
        return snapshot

    async def capture_window(self, window_id: str, bounds: Optional[Tuple[int, int, int, int]] = None) -> ScreenSnapshot:
        """Capture window frame region."""
        snapshot = await self.capture_engine.capture_window(window_id, bounds=bounds)
        self._publish_event(ScreenVisionEvent.SCREEN_CAPTURED, snapshot.to_dict())
        return snapshot

    async def capture_region(self, x: int, y: int, width: int, height: int) -> ScreenSnapshot:
        """Capture specific bounding rectangle region."""
        snapshot = await self.capture_engine.capture_region(x, y, width, height)
        self._publish_event(ScreenVisionEvent.SCREEN_CAPTURED, snapshot.to_dict())
        return snapshot

    async def analyze_screen(self, snapshot: Optional[ScreenSnapshot] = None) -> ScreenSnapshot:
        """
        Run full visual pipeline (OCR + Object Detection + Layout Tree) over frame snapshot.

        Returns:
            Fully analyzed ScreenSnapshot object.
        """
        target_snap = snapshot if snapshot else await self.capture_desktop()
        analyzed_snap = await self.ui_detector.analyze_snapshot(target_snap)

        self._publish_event(ScreenVisionEvent.OCR_COMPLETED, {"count": len(analyzed_snap.ocr_results)})
        self._publish_event(ScreenVisionEvent.UI_DETECTED, {"count": len(analyzed_snap.visual_elements)})

        return analyzed_snap

    def get_layout_tree(self, snapshot: ScreenSnapshot) -> LayoutNode:
        """Construct composite LayoutNode tree hierarchy."""
        return self.layout_analyzer.build_layout_tree(snapshot)

    async def verify_action_visuals(
        self,
        before_snapshot: ScreenSnapshot,
        action_name: str,
    ) -> VisualVerificationResult:
        """
        Capture post-action desktop frame and compare visual states.

        Returns:
            VisualVerificationResult object.
        """
        after_snapshot = await self.capture_desktop()
        is_changed = not self.cache.is_identical(after_snapshot.image_hash)
        diff_score = 0.25 if is_changed else 0.0

        res = VisualVerificationResult(
            changed=is_changed,
            diff_score=diff_score,
            action_name=action_name,
            message=f"Visual verification for '{action_name}': {'Changed' if is_changed else 'Unchanged'}",
            before_snapshot_id=before_snapshot.snapshot_id,
            after_snapshot_id=after_snapshot.snapshot_id,
        )

        self._publish_event(ScreenVisionEvent.VISUAL_VERIFICATION_COMPLETED, res.to_dict())
        return res

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        logger.info("Starting ScreenIntelligenceService...")

    def stop(self) -> None:
        logger.info("Stopping ScreenIntelligenceService...")
        self.cache.clear()

    def is_healthy(self) -> bool:
        return True

    def _publish_event(self, event: ScreenVisionEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish vision event '{event.value}': {e}")
