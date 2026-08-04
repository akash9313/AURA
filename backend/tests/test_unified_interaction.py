"""
Unified Interaction Engine Unit & Integration Tests.
Covers domain models, sub-20ms planner decision engine, priority ordering, strategy implementations,
fallback transitions, verification, and InteractionEngineService integration.
"""

import asyncio
import sys
import time
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, ".")

from interaction.models import (
    InteractionGoal,
    InteractionIntent,
    InteractionMethod,
    InteractionResult,
    InteractionTarget,
)
from interaction.events import InteractionEvent
from interaction.configuration import InteractionEngineConfig
from interaction.confidence import InteractionConfidenceScorer
from interaction.planner import InteractionPlanner
from interaction.fallback import FallbackManager
from interaction.verifier import InteractionVerifier
from interaction.executor import InteractionExecutor
from interaction.service import InteractionEngineService


# ==============================================================================
# Domain Models & Sub-20ms Planner Tests
# ==============================================================================

class TestInteractionModelsAndPlanner(unittest.TestCase):
    """Tests for Interaction domain models and sub-20ms planner decision engine."""

    def test_target_and_goal_serialization(self):
        target = InteractionTarget(name="Submit", automation_id="btn_submit")
        goal = InteractionGoal(intent=InteractionIntent.CLICK, target=target)
        d = goal.to_dict()

        self.assertEqual(d["intent"], "click")
        self.assertEqual(d["target"]["automation_id"], "btn_submit")

    def test_sub_20ms_planner_decision(self):
        planner = InteractionPlanner()
        goal = InteractionGoal(
            intent=InteractionIntent.CLICK,
            target=InteractionTarget(name="Save Button", automation_id="btn_save"),
        )

        start = time.time()
        candidates = planner.plan_interaction(goal)
        duration_ms = (time.time() - start) * 1000

        self.assertLess(duration_ms, 20.0)  # Verify sub-20ms target requirement
        self.assertEqual(candidates[0], InteractionMethod.UI_AUTOMATION)


# ==============================================================================
# Priority Order & Fallback Tests
# ==============================================================================

class TestPriorityOrderAndFallback(unittest.TestCase):
    """Tests for priority ordering and seamless strategy fallbacks."""

    def setUp(self):
        self.bus = MagicMock()
        self.fallback = FallbackManager(bus=self.bus)

    def test_priority_order_structure(self):
        planner = InteractionPlanner()
        goal = InteractionGoal(intent=InteractionIntent.CLICK)
        candidates = planner.plan_interaction(goal)

        self.assertIn(InteractionMethod.UI_AUTOMATION, candidates)
        self.assertIn(InteractionMethod.VISION, candidates)

    def test_fallback_transition(self):
        goal = InteractionGoal(goal_id="g_test_fallback")
        remaining = [InteractionMethod.BROWSER_DOM, InteractionMethod.KEYBOARD]

        next_method = self.fallback.handle_method_failure(
            goal=goal,
            failed_method=InteractionMethod.UI_AUTOMATION,
            reason="Control detached",
            remaining_candidates=remaining,
        )

        self.assertEqual(next_method, InteractionMethod.BROWSER_DOM)
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("method_failed", published)
        self.assertIn("method_switched", published)


# ==============================================================================
# Executor & Service Integration Tests
# ==============================================================================

class TestInteractionServiceIntegration(unittest.TestCase):
    """Integration tests for InteractionEngineService."""

    def setUp(self):
        self.bus = MagicMock()
        self.service = InteractionEngineService(bus=self.bus)

    def test_execute_click_goal(self):
        target = InteractionTarget(name="Submit Button", automation_id="btn_sub")
        res = asyncio.run(self.service.click(target=target))

        self.assertTrue(res.success)
        self.assertEqual(res.method_used, InteractionMethod.UI_AUTOMATION)
        self.assertEqual(res.fallback_count, 0)

    def test_execute_type_text_goal(self):
        target = InteractionTarget(name="Input Field")
        res = asyncio.run(self.service.type_text("Hello World", target=target))

        self.assertTrue(res.success)
        self.assertIsNotNone(res.method_used)


if __name__ == "__main__":
    unittest.main()
