import logging
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from cognition.models import GoalStatus, GoalType

logger = logging.getLogger("AURA.Cognition.GoalManager")


@dataclass
class Goal:
    """Represents a discrete user or system cognitive goal."""
    title: str
    goal_type: GoalType = GoalType.SHORT_TERM
    goal_id: str = field(default_factory=lambda: f"goal_{str(uuid.uuid4())[:8]}")
    status: GoalStatus = GoalStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "goal_type": self.goal_type.value,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }


class GoalManager:
    """
    Manager maintaining active, pending, dependent, background, and completed goal hierarchies.
    """

    def __init__(self):
        self._goals: Dict[str, Goal] = {}

    def create_goal(self, title: str, goal_type: GoalType = GoalType.SHORT_TERM, dependencies: List[str] = None) -> Goal:
        """Create and register a new goal."""
        goal = Goal(
            title=title,
            goal_type=goal_type,
            dependencies=dependencies or []
        )
        self._goals[goal.goal_id] = goal
        logger.info(f"Created goal '{goal.goal_id}': '{title}' [{goal_type.value}]")
        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def update_status(self, goal_id: str, status: GoalStatus) -> Optional[Goal]:
        goal = self.get_goal(goal_id)
        if goal:
            goal.status = status
            logger.info(f"Goal '{goal_id}' status updated to: '{status.value}'")
        return goal

    def get_active_goals(self) -> List[Goal]:
        return [g for g in self._goals.values() if g.status == GoalStatus.ACTIVE]


    def list_goals(self) -> List[Goal]:
        return list(self._goals.values())
