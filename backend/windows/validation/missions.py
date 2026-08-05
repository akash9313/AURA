"""
Desktop Test Mission Specifications.
Defines required test missions for validating desktop capabilities through the execution pipeline:
Mission 1: Launch Notepad -> Verify process running, verify window visible
Mission 2: Type 'Hello from AURA' -> Verify text exists
Mission 3: Launch Calculator -> Verify application ready
Mission 4: Switch back to Notepad -> Verify focused window
Mission 5: Close applications -> Verify processes terminated
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DesktopTestMissionSpec:
    """Specification of a desktop capability test mission."""
    mission_id: str
    name: str
    description: str
    user_request: str
    target_app: str
    capabilities_to_test: List[str]
    expected_process: str
    expected_window_title: str
    expected_text: Optional[str] = None
    input_parameters: Dict[str, Any] = field(default_factory=dict)


def get_default_desktop_test_missions() -> List[DesktopTestMissionSpec]:
    """Return standard desktop test missions required by system specification."""
    return [
        # Mission 1
        DesktopTestMissionSpec(
            mission_id="m1_launch_notepad",
            name="Mission 1: Launch Notepad",
            description="Launch Notepad application and verify process running and window visible",
            user_request="Launch Notepad app on Windows",
            target_app="notepad.exe",
            capabilities_to_test=["launch_application", "focus_window", "capture_window"],
            expected_process="notepad.exe",
            expected_window_title="Notepad",
        ),
        # Mission 2
        DesktopTestMissionSpec(
            mission_id="m2_type_text",
            name="Mission 2: Type Text in Notepad",
            description="Type 'Hello from AURA' in Notepad and verify text exists",
            user_request="Type 'Hello from AURA' into Notepad",
            target_app="notepad.exe",
            capabilities_to_test=["type_text", "read_ui_element", "copy_text", "paste_text"],
            expected_process="notepad.exe",
            expected_window_title="Notepad",
            expected_text="Hello from AURA",
            input_parameters={"text": "Hello from AURA"},
        ),
        # Mission 3
        DesktopTestMissionSpec(
            mission_id="m3_launch_calculator",
            name="Mission 3: Launch Calculator",
            description="Launch Calculator application and verify application ready",
            user_request="Launch Calculator app",
            target_app="calc.exe",
            capabilities_to_test=["launch_application", "click_control"],
            expected_process="calc.exe",
            expected_window_title="Calculator",
        ),
        # Mission 4
        DesktopTestMissionSpec(
            mission_id="m4_switch_window",
            name="Mission 4: Switch Window",
            description="Switch back to Notepad and verify focused window",
            user_request="Switch focus back to Notepad window",
            target_app="notepad.exe",
            capabilities_to_test=["switch_window", "focus_window"],
            expected_process="notepad.exe",
            expected_window_title="Notepad",
        ),
        # Mission 5
        DesktopTestMissionSpec(
            mission_id="m5_close_applications",
            name="Mission 5: Close Applications",
            description="Close open applications and verify processes terminated",
            user_request="Close Notepad and Calculator",
            target_app="notepad.exe",
            capabilities_to_test=["close_application"],
            expected_process="notepad.exe",
            expected_window_title="Closed",
        ),
    ]
