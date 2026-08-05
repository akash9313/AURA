import logging
from typing import List

from capabilities.models import Capability, CapabilityCategory
from capabilities.registry import CapabilityRegistry

logger = logging.getLogger("AURA.Capabilities.Loader")

BUILTIN_CAPABILITIES: List[Capability] = [
    Capability(
        capability_id="open_application",
        name="Open Application",
        description="Launches a desktop application by executable name or path",
        category=CapabilityCategory.APPLICATION,
        aliases=["launch_app", "run_app"],
    ),
    Capability(
        capability_id="browse_web",
        name="Browse Web",
        description="Navigates to a URL in the browser DOM engine",
        category=CapabilityCategory.BROWSER,
        aliases=["open_url", "navigate_browser"],
    ),
    Capability(
        capability_id="search_web",
        name="Search Web",
        description="Performs a web search for a query string",
        category=CapabilityCategory.BROWSER,
        aliases=["google_search", "web_search"],
    ),
    Capability(
        capability_id="click_button",
        name="Click Button",
        description="Clicks an interactive button or UI control element",
        category=CapabilityCategory.APPLICATION,
        aliases=["click_element", "press_button"],
    ),
    Capability(
        capability_id="read_pdf",
        name="Read PDF",
        description="Extracts text content from a PDF document",
        category=CapabilityCategory.DOCUMENT,
        aliases=["parse_pdf", "extract_pdf_text"],
    ),
    Capability(
        capability_id="write_file",
        name="Write File",
        description="Writes content or code to a file on disk",
        category=CapabilityCategory.FILESYSTEM,
        aliases=["create_file", "save_file"],
    ),
    Capability(
        capability_id="copy_text",
        name="Copy Text",
        description="Copies text snippet to the system clipboard",
        category=CapabilityCategory.SYSTEM,
        aliases=["clipboard_copy"],
    ),
    Capability(
        capability_id="summarize_document",
        name="Summarize Document",
        description="Summarizes text document using LLM cognitive engine",
        category=CapabilityCategory.REASONING,
        aliases=["summarize_text"],
    ),
    Capability(
        capability_id="answer_question",
        name="Answer Question",
        description="Generates answer to user question based on knowledge base",
        category=CapabilityCategory.REASONING,
        aliases=["ask_ai"],
    ),
    Capability(
        capability_id="create_project",
        name="Create Project",
        description="Initializes project workspace or template codebase",
        category=CapabilityCategory.TERMINAL,
        aliases=["init_project", "scaffold_app"],
    ),
    Capability(
        capability_id="run_terminal_command",
        name="Run Terminal Command",
        description="Executes shell or terminal command line in subprocess",
        category=CapabilityCategory.TERMINAL,
        aliases=["run_command", "exec_cmd"],
    ),
]


class CapabilityLoader:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def load_builtins(self) -> int:
        count = 0
        for cap in BUILTIN_CAPABILITIES:
            if self.registry.register(cap):
                count += 1
        return count
