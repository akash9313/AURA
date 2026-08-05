"""
AURA Desktop Capability Validation Subsystem (`backend/windows/validation/`).
Validates desktop capabilities through the complete execution pipeline without modifying desktop engines.
"""

from windows.validation.configuration import DesktopValidationConfig
from windows.validation.events import DesktopValidationEvent
from windows.validation.missions import DesktopTestMissionSpec, get_default_desktop_test_missions
from windows.validation.models import (
    DesktopMissionResult,
    DesktopTaskResult,
    DesktopValidationMetrics,
    DesktopValidationStatus,
)
from windows.validation.pipeline import DesktopValidationPipeline
from windows.validation.recovery import DesktopRecoveryStrategy, DesktopRecoveryValidator
from windows.validation.reporter import DesktopValidationReporter
from windows.validation.validator import DesktopCapabilityValidator
from windows.validation.verifier import DesktopVerificationEngine

__all__ = [
    "DesktopCapabilityValidator",
    "DesktopValidationPipeline",
    "DesktopVerificationEngine",
    "DesktopRecoveryValidator",
    "DesktopValidationReporter",
    "DesktopValidationConfig",
    "DesktopTestMissionSpec",
    "get_default_desktop_test_missions",
    "DesktopValidationStatus",
    "DesktopTaskResult",
    "DesktopMissionResult",
    "DesktopValidationMetrics",
    "DesktopValidationEvent",
    "DesktopRecoveryStrategy",
]
