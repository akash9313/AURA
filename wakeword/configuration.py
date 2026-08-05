from dataclasses import dataclass, field
from typing import List


@dataclass
class WakeWordConfig:
    wake_words: List[str] = field(default_factory=lambda: ["hey aura", "aura"])
    threshold: float = 0.5
    sample_rate: int = 16000
    chunk_size: int = 1280
    provider_name: str = "openwakeword"
    cooldown_sec: float = 2.0
    auto_restart_on_error: bool = True
