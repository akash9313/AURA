"""
Screen Intelligence Event Definitions.
Published to AURA EventBus during screen captures, OCR processing, UI detection, and visual verifications.
"""

from enum import Enum


class ScreenVisionEvent(Enum):
    """Event definitions for Screen Intelligence Engine."""
    SCREEN_CAPTURED = "screen_captured"
    OCR_COMPLETED = "ocr_completed"
    UI_DETECTED = "ui_detected"
    SCREEN_UPDATED = "screen_updated"
    VISUAL_VERIFICATION_COMPLETED = "visual_verification_completed"
