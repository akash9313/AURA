from dataclasses import dataclass


@dataclass
class StreamingLLMConfig:
    """Configurable settings for Streaming Gemini response engine."""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    top_p: float = 0.95
    max_output_tokens: int = 2048
    first_token_target_ms: float = 800.0
    streaming_enabled: bool = True
    system_prompt: str = "You are AURA, an advanced AI Operating System. Provide concise, direct, helpful responses."
    retry_count: int = 3
    timeout_seconds: float = 30.0
