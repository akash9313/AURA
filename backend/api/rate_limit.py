import logging
import time
from typing import Dict
from api.models import RateLimitRule

logger = logging.getLogger("AURA.API.RateLimit")


class APIRateLimiter:
    """Token bucket API rate limiter."""

    def __init__(self, rule: RateLimitRule = RateLimitRule()):
        self.rule = rule
        self.key_history: Dict[str, list] = {}

    def is_allowed(self, key_id: str) -> bool:
        now = time.time()
        window_start = now - 60.0

        if key_id not in self.key_history:
            self.key_history[key_id] = []

        # Retain only timestamps within the last 60 seconds
        self.key_history[key_id] = [t for t in self.key_history[key_id] if t > window_start]

        if len(self.key_history[key_id]) >= self.rule.requests_per_minute:
            logger.warning(f"Rate limit exceeded for API key '{key_id}' ({len(self.key_history[key_id])}/min)")
            return False

        self.key_history[key_id].append(now)
        return True
