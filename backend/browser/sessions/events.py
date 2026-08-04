from enum import Enum


class SessionEvent(Enum):
    """Event definitions for Browser Session Lifecycle & State Management."""
    SESSION_CREATED = "session_created"
    SESSION_LOADED = "session_loaded"
    SESSION_SAVED = "session_saved"
    SESSION_EXPIRED = "session_expired"
    SESSION_DESTROYED = "session_destroyed"
    SESSION_RESTORED = "session_restored"
