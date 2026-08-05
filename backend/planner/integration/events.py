"""
Planner Integration Event Definitions.
Published to EventBus during Mission lifecycle processing.
"""

from enum import Enum


class PlannerIntegrationEvent(Enum):
    """Event definitions for Planner Integration Subsystem."""
    MISSION_CREATED = "mission_created"
    MISSION_PLANNED = "mission_planned"
    MISSION_EXECUTION_REQUESTED = "mission_execution_requested"
    MISSION_COMPLETED = "mission_completed"
    MISSION_FAILED = "mission_failed"
