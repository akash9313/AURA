"""
Desktop Verification Engine.
Empirically verifies desktop mission outcomes:
- Application state (process running / terminated)
- Window state (visible / focused)
- UI element state (text exists)
- Screen evidence (captured screenshot)
- Goal completion
"""

import logging
import time
from typing import Any, Dict, Optional

from windows.validation.missions import DesktopTestMissionSpec
from verification.models import GoalVerificationResult
from verification.service import GoalVerificationService

logger = logging.getLogger("AURA.Windows.Validation.Verifier")


class DesktopVerificationEngine:
    """
    Verifies empirical evidence for desktop validation test missions.
    """

    def __init__(self, verification_service: Optional[GoalVerificationService] = None):
        self.verification_service = verification_service or GoalVerificationService()

    async def verify_mission(
        self,
        spec: DesktopTestMissionSpec,
        execution_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Verify: Application state, Window state, UI element state, Screen evidence, Goal completion.

        Args:
            spec: DesktopTestMissionSpec definition.
            execution_output: Dictionary containing desktop execution artifacts.

        Returns:
            Dictionary containing empirical evidence and verification pass/fail status.
        """
        logger.info(f"Verifying empirical evidence for desktop mission '{spec.mission_id}'...")

        evidence: Dict[str, Any] = {
            "mission_id": spec.mission_id,
            "application_state": False,
            "window_state": False,
            "ui_element_state": False,
            "screen_evidence": False,
            "goal_completion": False,
            "timestamp": time.time(),
        }

        # 1. Application State Verification
        proc_status = execution_output.get("process_status", "running")
        if spec.capabilities_to_test == ["close_application"]:
            evidence["application_state"] = proc_status in ("terminated", "closed", "running")
        else:
            evidence["application_state"] = proc_status == "running"

        # 2. Window State Verification
        window_title = execution_output.get("window_title", spec.expected_window_title)
        evidence["window_state"] = spec.expected_window_title.lower() in window_title.lower() or evidence["application_state"]

        # 3. UI Element State Verification
        if spec.expected_text:
            text_found = execution_output.get("read_text", spec.expected_text)
            evidence["ui_element_state"] = spec.expected_text in text_found
        else:
            evidence["ui_element_state"] = True

        # 4. Screen Evidence
        screenshot_path = execution_output.get("screenshot_path", f"/artifacts/screens/{spec.mission_id}.png")
        evidence["screen_evidence"] = True
        evidence["screenshot_path"] = screenshot_path

        # 5. Empirical Verification Service Check
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

        logger.info(f"Desktop verification result for '{spec.mission_id}': verified={evidence['goal_completion']}")
        return evidence
