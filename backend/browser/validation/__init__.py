"""
AURA Browser Capability Validation Subsystem (`backend/browser/validation/`).
Validates browser capabilities through the complete execution pipeline without modifying Browser Engine.
"""

from browser.validation.configuration import BrowserValidationConfig
from browser.validation.events import BrowserValidationEvent
from browser.validation.missions import BrowserTestMissionSpec, get_default_test_missions
from browser.validation.models import (
    CapabilityValidationResult,
    CapabilityValidationStatus,
    MissionValidationResult,
    ValidationMetrics,
)
from browser.validation.pipeline import ValidationPipeline
from browser.validation.recovery import BrowserRecoveryValidator, RecoveryStrategy
from browser.validation.reporter import ValidationReporter
from browser.validation.validator import BrowserCapabilityValidator
from browser.validation.verifier import BrowserVerificationEngine

__all__ = [
    "BrowserCapabilityValidator",
    "ValidationPipeline",
    "BrowserVerificationEngine",
    "BrowserRecoveryValidator",
    "ValidationReporter",
    "BrowserValidationConfig",
    "BrowserTestMissionSpec",
    "get_default_test_missions",
    "CapabilityValidationStatus",
    "CapabilityValidationResult",
    "MissionValidationResult",
    "ValidationMetrics",
    "BrowserValidationEvent",
    "RecoveryStrategy",
]
