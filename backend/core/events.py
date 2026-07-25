from enum import Enum

class Event(Enum):

    TEXT_READY = "text_ready"

    INTENT_READY = "intent_ready"

    ACTION_READY = "action_ready"

    AI_RESPONSE_READY = "ai_response_ready"

    SHUTDOWN = "shutdown"