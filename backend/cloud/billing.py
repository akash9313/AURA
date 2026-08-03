import logging

logger = logging.getLogger("AURA.Cloud.Billing")


class BillingManager:
    """Manages cloud subscription tiers and usage metrics."""

    def get_subscription_tier(self, user_id: str) -> str:
        return "pro"
