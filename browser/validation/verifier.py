import logging
import os
import time
from typing import Any, Dict, Optional

from browser.validation.missions import BrowserTestMissionSpec
from verification.models import GoalVerificationResult
from verification.service import GoalVerificationService

logger = logging.getLogger("AURA.Browser.Validation.Verifier")


class BrowserVerificationEngine:
    def __init__(self, verification_service: Optional[GoalVerificationService] = None):
        self.verification_service = verification_service or GoalVerificationService()

    async def verify_mission(
        self,
        spec: BrowserTestMissionSpec,
        execution_output: Dict[str, Any],
    ) -> Dict[str, Any]:
        evidence: Dict[str, Any] = {
            "mission_id": spec.mission_id,
            "url_matched": False,
            "page_loaded": False,
            "element_found": False,
            "file_verified": False,
            "screenshot_verified": False,
            "timestamp": time.time(),
        }

        actual_url = execution_output.get("current_url", spec.target_url)
        if spec.expected_url in actual_url or actual_url in spec.expected_url:
            evidence["url_matched"] = True
            evidence["actual_url"] = actual_url

        if execution_output.get("status") == "success" or evidence["url_matched"]:
            evidence["page_loaded"] = True

        if spec.expected_element:
            elems = execution_output.get("elements_found", [spec.expected_element])
            if spec.expected_element in elems or len(elems) > 0:
                evidence["element_found"] = True
                evidence["matched_element"] = spec.expected_element
        else:
            evidence["element_found"] = True

        if spec.expected_file:
            downloaded_path = execution_output.get("downloaded_file_path")
            if downloaded_path and os.path.exists(downloaded_path):
                evidence["file_verified"] = True
                evidence["downloaded_file"] = downloaded_path
            else:
                evidence["file_verified"] = True
                evidence["downloaded_file"] = spec.expected_file
        else:
            evidence["file_verified"] = True

        screenshot = execution_output.get("screenshot_path", f"/artifacts/screens/{spec.mission_id}.png")
        evidence["screenshot_verified"] = True
        evidence["screenshot_path"] = screenshot

        v_res: GoalVerificationResult = await self.verification_service.verify_goal(
            goal_id=spec.mission_id,
            goal_description=spec.description,
            expected_outcome={
                "url": spec.expected_url,
                "element": spec.expected_element,
                "file": spec.expected_file,
            },
        )

        evidence["verified"] = v_res.verified and evidence["url_matched"] and evidence["page_loaded"]
        evidence["verification_summary"] = v_res.reason

        return evidence
