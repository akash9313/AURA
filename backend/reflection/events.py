"""
Reflection Event Definitions.
Published to AURA EventBus during reflection analysis, pattern detection, and recommendation generation.
"""

from enum import Enum


class ReflectionEvent(Enum):
    """Event definitions for Reflection Engine."""
    REFLECTION_STARTED = "reflection_started"
    REFLECTION_COMPLETED = "reflection_completed"
    PATTERN_DETECTED = "pattern_detected"
    RECOMMENDATION_CREATED = "recommendation_created"
    WORKFLOW_ANALYZED = "workflow_analyzed"
