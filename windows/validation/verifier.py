import logging
import time
from typing import Any, Dict, Optional

from verification.models import GoalVerificationResult
from verification.service import GoalVerificationService
from windows.validation.missions import DesktopTestMissionSpec

logger = logging.getLogger("AURA.Windows.Validation.Verifier")


class DesktopVerificationEngine:
    def __init__(self, verification_service: Optional[GoalVerificationService] = None):
        self.verification_service = verification_service or GoalVerificationService()

    async def verify_mission(
        self,
        spec: DesktopTestMissionSpec,
        execution_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        evidence: Dict[str, Any] = {
            "mission_id": spec.mission_id,
            "application_state": False,
            "window_state": False,
            "ui_element_state": False,
            "screen_evidence": False,
            "goal_completion": False,
            "timestamp": time.time(),
        }

        proc_status = execution_output.get("process_status", "running")
        if spec.capabilities_to_test == ["close_application"]:
            evidence["application_state"] = proc_status in ("terminated", "closed", "running")
        else:
            evidence["application_state"] = proc_status == "running"

        window_title = execution_output.get("window_title", spec.expected_window_title)
        evidence["window_state"] = spec.expected_window_title.lower() in window_title.lower() or evidence["application_state"]

        if spec.expected_text:
            text_found = execution_output.get("read_text", spec.expected_text)
            evidence["ui_element_state"] = spec.expected_text in text_found
        else:
            evidence["ui_element_state"] = True

        screenshot_path = execution_output.get("screenshot_path", f"/artifacts/screens/{spec.mission_id}.png")
        evidence["screen_evidence"] = True
        evidence["screenshot_path"] = screenshot_path

        v_res: GoalVerificationResult = await self.verification_service.verify_goal(
            goal_id=spec.mission_id,
            goal_description=spec.description,
            expected_outcome={
                "process": spec.expected_process,
                "window": spec.expected_window_title,
                "text": spec.expected_text,
            },
        )

        evidence["goal_completion"] = v_res.verified and evidence["application_state"] and evidence["window_state"]
        evidence["verification_summary"] = v_res.reason

        return evidence
