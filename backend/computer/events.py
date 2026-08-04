"""
Computer Subsystem Event Definitions.
Published to AURA EventBus during service lifecycle and provider events.
"""

from enum import Enum


class ComputerEvent(Enum):
    """Event definitions for Computer Service & Desktop Automation Subsystem."""
    COMPUTER_STARTED = "computer_started"
    COMPUTER_READY = "computer_ready"
    COMPUTER_STOPPED = "computer_stopped"
    PROVIDER_LOADED = "provider_loaded"
    PROVIDER_FAILED = "provider_failed"
