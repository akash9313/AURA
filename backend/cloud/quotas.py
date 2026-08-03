import logging
from typing import Dict
from cloud.models import CloudQuota

logger = logging.getLogger("AURA.Cloud.Quotas")


class QuotaManager:
    """Tracks cloud storage and API rate limit quotas per account."""

    def __init__(self):
        self.quotas: Dict[str, CloudQuota] = {}

    def get_quota(self, user_id: str) -> CloudQuota:
        if user_id not in self.quotas:
            self.quotas[user_id] = CloudQuota(user_id=user_id)
        return self.quotas[user_id]
