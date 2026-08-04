from dataclasses import dataclass


@dataclass
class STTConfig:
    """Configurable settings for Streaming Speech-to-Text engine."""
    model_name: str = "base"
    language: str = "en"
    auto_detect_language: bool = True
    chunk_size: int = 1024
    beam_size: int = 5
    temperature: float = 0.0
    compute_device: str = "cpu"
    partial_latency_target_ms: float = 300.0
    final_latency_target_ms: float = 700.0
    max_utterance_duration_seconds: float = 30.0
