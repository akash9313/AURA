"""
Conversation Manager Configuration.
Configures follow-up timeouts, max duration boundaries, silence limits, and interrupt sensitivity.
"""

from dataclasses import dataclass


@dataclass
class ConversationConfig:
    """Configuration parameters for Conversation Manager Subsystem."""
    followup_timeout_sec: float = 5.0
    max_conversation_duration_sec: float = 300.0
    max_silence_duration_sec: float = 10.0
    interrupt_sensitivity: float = 0.7
    enable_followup_mode: bool = True
