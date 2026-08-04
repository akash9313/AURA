from enum import Enum


class InteractionEvent(Enum):
    INTERACTION_STARTED = "interaction_started"
    METHOD_SELECTED = "method_selected"
    METHOD_FAILED = "method_failed"
    METHOD_SWITCHED = "method_switched"
    INTERACTION_COMPLETED = "interaction_completed"
