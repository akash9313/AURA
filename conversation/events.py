from enum import Enum


class ConversationEvent(Enum):
    CONVERSATION_STARTED = "conversation_started"
    LISTENING_STARTED = "listening_started"
    TRANSCRIPTION_COMPLETED = "transcription_completed"
    LLM_STARTED = "llm_started"
    LLM_COMPLETED = "llm_completed"
    TTS_STARTED = "tts_started"
    TTS_COMPLETED = "tts_completed"
    CONVERSATION_ENDED = "conversation_ended"
    CONVERSATION_INTERRUPTED = "conversation_interrupted"

    USER_INTERRUPTED = "user_interrupted"
    LLM_CANCELLED = "llm_cancelled"
    TTS_CANCELLED = "tts_cancelled"
    AUDIO_QUEUE_FLUSHED = "audio_queue_flushed"
    CONVERSATION_RESUMED = "conversation_resumed"
    CONVERSATION_CANCELLED = "conversation_cancelled"
