from dataclasses import dataclass, field
from typing import List


@dataclass
class TTSConfig:
    """Configurable settings for Streaming Text-to-Speech synthesis."""
    voice_name: str = "en-US-AvaNeural"
    speaking_rate: float = 1.0
    volume: float = 1.0
    playback_start_latency_target_ms: float = 1000.0
    sentence_delimiters: List[str] = field(default_factory=lambda: [".", "!", "?", "\n", ";"])
    max_sentence_length_chars: int = 150
    queue_max_size: int = 50
    provider_name: str = "edge"
