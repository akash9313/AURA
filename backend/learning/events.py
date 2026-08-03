from enum import Enum


class LearningEvent(Enum):
    """Lifecycle event definitions for Adaptive Intelligence Engine."""
    PREFERENCE_UPDATED = "preference_updated"
    WORKFLOW_LEARNED = "workflow_learned"
    WORKFLOW_OPTIMIZED = "workflow_optimized"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    CONFIDENCE_UPDATED = "confidence_updated"
    LEARNING_COMPLETED = "learning_completed"
