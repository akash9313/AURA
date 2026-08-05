"""
AI Planner Event Definitions.
Published to AURA EventBus during mission planning, plan updates, failures, and mission launch events.
"""

from enum import Enum


class PlannerEvent(Enum):
    """Event definitions for AI Planner Engine."""
    PLAN_CREATED = "plan_created"
    PLAN_UPDATED = "plan_updated"
    PLAN_FAILED = "plan_failed"
    MISSION_STARTED = "mission_started"
