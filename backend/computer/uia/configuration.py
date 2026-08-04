"""
UI Automation Engine Configuration.
Configures lookup latency thresholds, caching policies, and tree depth caps.
"""

from dataclasses import dataclass


@dataclass
class UIAutomationConfig:
    """Configuration parameters for UI Automation Subsystem."""
    element_lookup_timeout_ms: float = 100.0
    cache_ttl_seconds: float = 5.0
    max_tree_depth: int = 15
    max_cached_elements: int = 1000
    enable_smart_cache: bool = True
    auto_verify_actions: bool = True
