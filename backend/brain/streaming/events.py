from enum import Enum


class StreamingLLMEvent(Enum):
    """Event definitions for Streaming LLM Response Engine."""
    LLM_STARTED = "llm_started"
    LLM_PARTIAL_TOKEN = "llm_partial_token"
    LLM_PARTIAL_RESPONSE = "llm_partial_response"
    LLM_FINISHED = "llm_finished"
    LLM_CANCELLED = "llm_cancelled"
    LLM_ERROR = "llm_error"
