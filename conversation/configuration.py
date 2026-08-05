from dataclasses import dataclass


@dataclass
class ConversationConfig:
    followup_timeout_sec: float = 5.0
    max_conversation_duration_sec: float = 300.0
    max_silence_duration_sec: float = 10.0
    interrupt_sensitivity: float = 0.7
    enable_followup_mode: bool = True
