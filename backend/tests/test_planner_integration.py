"""
Planner Integration Unit, Integration, Mission Creation, and Failure Handling Test Suite.
Tests RequestParser, MissionBuilder, ResponseFormatter, PlannerClient, and PlannerIntegrationService.
"""

import asyncio
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, ".")

from planner.integration.models import (
    Mission,
    MissionExecutionMode,
    MissionPriority,
    MissionRequest,
    MissionStatus,
)
from planner.integration.events import PlannerIntegrationEvent
from planner.integration.configuration import PlannerIntegrationConfig
from planner.integration.request_parser import RequestParser
from planner.integration.mission_builder import MissionBuilder
from planner.integration.response_formatter import ResponseFormatter
from planner.integration.planner_client import PlannerClient
from planner.integration.planner_service import PlannerIntegrationService
from planner.models import MissionPlan, PlanningResult, TaskGraph, PlannerTask


class TestPlannerIntegration(unittest.TestCase):
    """Test suite for Planner Integration subsystem."""

    def setUp(self):
        self.bus = MagicMock()
        self.config = PlannerIntegrationConfig(planner_timeout_sec=1.0, max_retries=1)
        self.parser = RequestParser()
        self.builder = MissionBuilder()
        self.formatter = ResponseFormatter(self.config)

    def test_request_parser_sanitization_and_priority(self):
        """Test transcript parsing, whitespace sanitization, and priority extraction."""
        req = self.parser.parse_request("   Urgent: Open Notepad immediately  ")
        self.assertEqual(req.original_user_request, "Urgent: Open Notepad immediately")
        self.assertEqual(req.priority, MissionPriority.HIGH)

        # Empty transcript raises ValueError
        with self.assertRaises(ValueError):
            self.parser.parse_request("    ")

    def test_mission_builder(self):
        """Test constructing Mission from request and MissionPlan."""
        req = self.parser.parse_request("Open Notepad")
        task = PlannerTask(description="Open Notepad app", capability_required="open_app")
        graph = TaskGraph()
        graph.add_task(task)
        plan = MissionPlan(user_request="Open Notepad", goal_summary="Open Notepad", task_graph=graph)

        mission = self.builder.build_mission(req, plan=plan)
        self.assertEqual(mission.goal, "Open Notepad")
        self.assertEqual(mission.status, MissionStatus.PLANNED)
        self.assertIn("open_app", mission.required_capabilities)

    def test_response_formatter(self):
        """Test formatting completed and failed Mission outcomes."""
        req = self.parser.parse_request("Test prompt")
        mission_comp = self.builder.build_mission(req)
        mission_comp.status = MissionStatus.COMPLETED
        mission_comp.result_data = {"output": "Notepad opened successfully."}
        res_text = self.formatter.format_response(mission_comp)
        self.assertEqual(res_text, "Notepad opened successfully.")

        mission_fail = self.builder.build_mission(req, error_message="Capability missing")
        fail_text = self.formatter.format_response(mission_fail)
        self.assertIn("Capability missing", fail_text)

    def test_planner_service_full_flow(self):
        """Test PlannerIntegrationService complete end-to-end request processing flow."""
        mock_client = MagicMock()
        
        # Mock generate_plan
        task = PlannerTask(description="Open Notepad", capability_required="open_app")
        graph = TaskGraph()
        graph.add_task(task)
        plan = MissionPlan(user_request="Open Notepad", goal_summary="Open Notepad", task_graph=graph)
        mock_client.generate_plan = AsyncMock(return_value=PlanningResult(success=True, plan=plan, message="OK"))

        # Mock execute_mission
        mock_client.execute_mission = AsyncMock(return_value={"success": True, "workflow_id": "wf_123", "completed_tasks": ["task_1"]})

        service = PlannerIntegrationService(bus=self.bus, config=self.config, planner_client=mock_client)

        mission = asyncio.run(service.process_request("Open Notepad"))

        self.assertEqual(mission.status, MissionStatus.COMPLETED)

        # Verify events published to EventBus
        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_created", published)
        self.assertIn("mission_planned", published)
        self.assertIn("mission_execution_requested", published)
        self.assertIn("mission_completed", published)
        self.assertIn("ai_response_ready", published)

    def test_planner_failure_handling(self):
        """Test failure handling when planning or execution fails."""
        mock_client = MagicMock()
        mock_client.generate_plan = AsyncMock(return_value=PlanningResult(success=False, plan=None, message="Planner error"))

        service = PlannerIntegrationService(bus=self.bus, config=self.config, planner_client=mock_client)
        mission = asyncio.run(service.process_request("Unrecognized command"))

        self.assertEqual(mission.status, MissionStatus.FAILED)
        self.assertEqual(mission.error_message, "Planner error")

        published = [call[0][0] for call in self.bus.publish.call_args_list]
        self.assertIn("mission_failed", published)


if __name__ == "__main__":
    unittest.main()
