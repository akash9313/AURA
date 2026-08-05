from dataclasses import dataclass


@dataclass
class PlannerIntegrationConfig:
    planner_timeout_sec: float = 10.0
    max_planning_duration_sec: float = 30.0
    max_retries: int = 2
    backoff_sec: float = 1.0
    fallback_response: str = "I apologize, but I was unable to convert your request into an executable mission."
    auto_execute: bool = True
