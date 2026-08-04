"""
Goal Verification Engine Configuration.
Configures confidence thresholds, timeouts, and recovery policies.
"""

from dataclasses import dataclass


@dataclass
class GoalVerificationConfig:
    """Configuration parameters for Goal Verification Subsystem."""
    default_confidence_threshold: float = 0.75
    verification_timeout_ms: float = 5000.0
    auto_recovery_enabled: bool = True
    max_retry_attempts: int = 2
    require_multi_source_evidence: bool = False
