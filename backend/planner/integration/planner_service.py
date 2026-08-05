"""
Planner Integration Service.
Top-level AURA service integrating AIPlanner and WorkflowExecutor into the Conversation Manager lifecycle.
Converts every user request into a Mission and orchestrates planning and execution via EventBus.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

from core.service import Service
from planner.integration.configuration import PlannerIntegrationConfig
from planner.integration.events import PlannerIntegrationEvent
from planner.integration.mission_builder import MissionBuilder
from planner.integration.models import Mission, MissionStatus
from planner.integration.planner_client import PlannerClient
from planner.integration.request_parser import RequestParser
from planner.integration.response_formatter import ResponseFormatter

logger = logging.getLogger("AURA.Planner.Integration.Service")


class PlannerIntegrationService(Service):
    """
    Service wrapper connecting Planner Integration Engine to EventBus.
    Converts transcripts into Missions, calls Planner, forwards to WorkflowExecutor,
    and returns formatted results to Conversation Manager.
    """

    def __init__(
        self,
        bus: Any = None,
        config: Optional[PlannerIntegrationConfig] = None,
        planner_client: Optional[PlannerClient] = None,
    ):
        super().__init__(bus)
        self.config = config or PlannerIntegrationConfig()
        self.planner_client = planner_client or PlannerClient(config=self.config)
        self.request_parser = RequestParser()
        self.mission_builder = MissionBuilder()
        self.response_formatter = ResponseFormatter(config=self.config)

        logger.info("PlannerIntegrationService initialized")

    def start(self) -> None:
        """Start service and subscribe to EventBus transcript channels."""
        logger.info("Starting PlannerIntegrationService...")
        if self.bus:
            self.bus.subscribe("TEXT_READY", self._on_user_transcript)
            self.bus.subscribe("final_transcript", self._on_user_transcript)
            self.bus.subscribe("user_transcript", self._on_user_transcript)
            self.bus.subscribe("GOAL_CREATED", self._on_goal_created)

    def stop(self) -> None:
        """Stop PlannerIntegrationService."""
        logger.info("Stopping PlannerIntegrationService...")

    def is_healthy(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Event Handlers & Orchestration
    # ------------------------------------------------------------------

    def _on_user_transcript(self, payload: Any) -> None:
        """Handle incoming transcript event synchronously or as async task."""
        text = ""
        if isinstance(payload, dict):
            text = payload.get("text", payload.get("goal", ""))
        else:
            text = str(payload)

        if text:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.process_request(text))
            except RuntimeError:
                asyncio.run(self.process_request(text))

    def _on_goal_created(self, payload: Any) -> None:
        self._on_user_transcript(payload)

    async def process_request(self, raw_transcript: str, context: Optional[Dict[str, Any]] = None) -> Mission:
        """
        Complete processing flow:
        Receive transcript -> RequestParser -> MISSION_CREATED -> AIPlanner -> MISSION_PLANNED ->
        WorkflowExecutor -> MISSION_EXECUTION_REQUESTED -> MISSION_COMPLETED / MISSION_FAILED -> ResponseFormatter.

        Args:
            raw_transcript: User prompt text.
            context: Environment context dictionary.

        Returns:
            Processed Mission object.
        """
        logger.info(f"Processing user request into Mission: '{raw_transcript}'...")

        # 1. Parse Request
        try:
            req = self.request_parser.parse_request(raw_transcript, context)
        except ValueError as e:
            msg = f"Invalid request: {str(e)}"
            logger.warning(msg)
            err_mission = Mission(
                original_user_request=raw_transcript,
                status=MissionStatus.FAILED,
                error_message=msg,
            )
            self._publish_event(PlannerIntegrationEvent.MISSION_FAILED, err_mission.to_dict())
            self._send_response_to_conversation(self.response_formatter.format_response(err_mission))
            return err_mission

        # 2. Build Initial Mission & Publish MISSION_CREATED
        mission = self.mission_builder.build_mission(req)
        self._publish_event(PlannerIntegrationEvent.MISSION_CREATED, mission.to_dict())

        # 3. Request Plan from AIPlanner
        plan_result = await self.planner_client.generate_plan(req)

        if not plan_result.success or not plan_result.plan:
            err_msg = plan_result.message
            logger.error(f"Planning failed for mission '{mission.mission_id}': {err_msg}")
            mission.status = MissionStatus.FAILED
            mission.error_message = err_msg
            self._publish_event(PlannerIntegrationEvent.MISSION_FAILED, mission.to_dict())
            self._send_response_to_conversation(self.response_formatter.format_response(mission))
            return mission

        # 4. Update Mission with Plan & Publish MISSION_PLANNED
        mission = self.mission_builder.build_mission(req, plan=plan_result.plan)
        mission.status = MissionStatus.PLANNED
        self._publish_event(PlannerIntegrationEvent.MISSION_PLANNED, mission.to_dict())

        if not self.config.auto_execute:
            logger.info(f"Auto-execute disabled. Mission '{mission.mission_id}' remains in PLANNED state.")
            return mission

        # 5. Publish MISSION_EXECUTION_REQUESTED & Execute via WorkflowExecutor
        mission.status = MissionStatus.EXECUTING
        self._publish_event(PlannerIntegrationEvent.MISSION_EXECUTION_REQUESTED, mission.to_dict())

        try:
            exec_outcome = await self.planner_client.execute_mission(mission)
            if exec_outcome.get("success", False):
                mission.status = MissionStatus.COMPLETED
                mission.result_data = exec_outcome
                mission.completed_at = time.time()
                logger.info(f"Mission '{mission.mission_id}' completed successfully!")
                self._publish_event(PlannerIntegrationEvent.MISSION_COMPLETED, mission.to_dict())
            else:
                mission.status = MissionStatus.FAILED
                mission.error_message = exec_outcome.get("error", "Workflow execution failed")
                logger.error(f"Mission '{mission.mission_id}' execution failed: {mission.error_message}")
                self._publish_event(PlannerIntegrationEvent.MISSION_FAILED, mission.to_dict())

        except Exception as e:
            err_str = f"Workflow execution exception: {str(e)}"
            logger.error(err_str)
            mission.status = MissionStatus.FAILED
            mission.error_message = err_str
            self._publish_event(PlannerIntegrationEvent.MISSION_FAILED, mission.to_dict())

        # 6. Format response and notify Conversation Manager / TTS
        response_text = self.response_formatter.format_response(mission)
        self._send_response_to_conversation(response_text)

        return mission

    def _send_response_to_conversation(self, response_text: str) -> None:
        """Publish formatted response event for Conversation Manager & TTS."""
        if self.bus:
            self.bus.publish("ai_response_ready", {"text": response_text})
            self.bus.publish("speech_ready", {"text": response_text})

    def _publish_event(self, event: PlannerIntegrationEvent, data: Dict[str, Any]) -> None:
        if self.bus:
            try:
                self.bus.publish(event.value, data)
            except Exception as e:
                logger.error(f"Failed to publish planner integration event '{event.value}': {e}")
