from dataclasses import dataclass


@dataclass
class InteractionEngineConfig:
    selection_timeout_ms: float = 20.0
    max_fallback_attempts: int = 4
    auto_verify: bool = True
    enable_vision_fallback: bool = True
