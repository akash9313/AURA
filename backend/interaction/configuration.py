"""
Interaction Engine Configuration.
Configures sub-20ms selection latency targets, fallback attempt caps, and auto-verification policies.
"""

from dataclasses import dataclass


@dataclass
class InteractionEngineConfig:
    """Configuration parameters for Interaction Engine Subsystem."""
    selection_timeout_ms: float = 20.0
    max_fallback_attempts: int = 4
    auto_verify: bool = True
    enable_vision_fallback: bool = True
