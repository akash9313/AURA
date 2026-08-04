from enum import Enum


class ScreenVisionEvent(Enum):
    SCREEN_CAPTURED = "screen_captured"
    OCR_COMPLETED = "ocr_completed"
    UI_DETECTED = "ui_detected"
    SCREEN_UPDATED = "screen_updated"
    VISUAL_VERIFICATION_COMPLETED = "visual_verification_completed"
