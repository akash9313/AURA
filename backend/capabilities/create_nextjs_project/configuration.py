"""
create_nextjs_project Capability Configuration.
Configures default paths, localhost ports, timeouts, and executable names.
"""

import os
from dataclasses import dataclass, field


@dataclass
class CreateNextJsConfig:
    """Configuration parameters for Next.js project creation capability."""
    default_parent_directory: str = field(default_factory=lambda: os.path.abspath(os.path.expanduser("~/Documents")))
    localhost_port: int = 3000
    max_wait_localhost_sec: float = 30.0
    vscode_executable: str = "code"
    auto_open_browser: bool = True
    max_retries: int = 3
