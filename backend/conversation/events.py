from enum import Enum


class ConversationEvent(Enum):
    """Event definitions for Full Duplex Conversation and Interruption."""
    USER_INTERRUPTED = "user_interrupted"
    LLM_CANCELLED = "llm_cancelled"
    TTS_CANCELLED = "tts_cancelled"
    AUDIO_QUEUE_FLUSHED = "audio_queue_flushed"
    CONVERSATION_RESUMED = "conversation_resumed"
    CONVERSATION_CANCELLED = "conversation_cancelled"
