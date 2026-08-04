import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("AURA.Browser.Sessions.Permissions")


class SessionPermissionManager:
    """
    Manages Security Permissions and Domain Policy Enforcement for Browser Sessions.
    """

    def __init__(self, allowed_domains: Optional[List[str]] = None):
        self.allowed_domains = allowed_domains or []

    def is_domain_allowed(self, domain: str) -> bool:
        if not self.allowed_domains:
            return True  # No restriction
        return any(allowed in domain for allowed in self.allowed_domains)

    def validate_access(self, domain: str) -> bool:
        allowed = self.is_domain_allowed(domain)
        if not allowed:
            logger.warning(f"Session access denied to domain '{domain}' by security policy.")
        return allowed
