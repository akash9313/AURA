from dataclasses import dataclass


@dataclass
class VADConfig:
    """Configurable parameters for Voice Activity Detection."""
    energy_threshold: float = 300.0
    sensitivity: float = 0.5  # 0.0 (least sensitive) to 1.0 (most sensitive)
    min_speech_duration_ms: float = 100.0  # minimum speech duration to trigger VOICE_STARTED
    min_silence_duration_ms: float = 400.0  # minimum silence duration to trigger VOICE_ENDED
    speech_timeout_seconds: float = 10.0
    sample_rate: int = 16000
    frame_duration_ms: float = 20.0
    adaptive_noise_floor: bool = True
