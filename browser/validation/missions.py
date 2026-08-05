from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BrowserTestMissionSpec:
    mission_id: str
    name: str
    description: str
    user_request: str
    target_url: str
    capabilities_to_test: List[str]
    expected_url: str
    expected_element: Optional[str] = None
    expected_file: Optional[str] = None
    input_parameters: Dict[str, Any] = field(default_factory=dict)


def get_default_test_missions() -> List[BrowserTestMissionSpec]:
    return [
        BrowserTestMissionSpec(
            mission_id="m1_open_website",
            name="Mission 1: Open Website & Navigation",
            description="Open https://example.com and verify page is loaded",
            user_request="Open https://example.com in browser and capture screenshot",
            target_url="https://example.com",
            capabilities_to_test=["open_website", "navigate", "capture_screenshot", "extract_article"],
            expected_url="https://example.com",
            expected_element="h1",
        ),
        BrowserTestMissionSpec(
            mission_id="m2_search",
            name="Mission 2: Web Search",
            description="Search for 'Artificial Intelligence' and verify search results exist",
            user_request="Search the web for Artificial Intelligence",
            target_url="https://www.google.com",
            capabilities_to_test=["search", "extract_table", "navigate"],
            expected_url="google.com",
            expected_element="form",
            input_parameters={"query": "Artificial Intelligence"},
        ),
        BrowserTestMissionSpec(
            mission_id="m3_fill_form",
            name="Mission 3: Form Completion & Submission",
            description="Fill sample form and verify submission confirmation",
            user_request="Fill out and submit sample web form",
            target_url="https://httpbin.org/forms/post",
            capabilities_to_test=["fill_form", "submit_form", "upload_file"],
            expected_url="httpbin.org",
            expected_element="input",
            input_parameters={"username": "AURA_Test_User", "comments": "Automated validation"},
        ),
        BrowserTestMissionSpec(
            mission_id="m4_download_file",
            name="Mission 4: File Download",
            description="Download file and verify file exists on local storage",
            user_request="Download sample file from server",
            target_url="https://httpbin.org/bytes/1024",
            capabilities_to_test=["download_file"],
            expected_url="httpbin.org",
            expected_file="sample_download.bin",
        ),
    ]
