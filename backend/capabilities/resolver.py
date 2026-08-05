"""
Capability Resolver Engine.
Resolves capability requests, manages version compatibility, deprecations, replacements, and aliases.
"""

import logging
from typing import Optional

from capabilities.configuration import CapabilityConfig
from capabilities.models import Capability
from capabilities.registry import CapabilityRegistry

logger = logging.getLogger("AURA.Capabilities.Resolver")


class CapabilityResolver:
    """
    Resolves requested capability IDs/aliases to active, compatible Capability models.
    """

    def __init__(self, registry: CapabilityRegistry, config: Optional[CapabilityConfig] = None):
        self.registry = registry
        self.config = config or CapabilityConfig()

    def resolve(self, capability_id_or_alias: str) -> Optional[Capability]:
        """
        Resolve capability by ID or alias, enforcing versioning, deprecation redirects, and platform rules.

        Args:
            capability_id_or_alias: Capability ID or alias string.

        Returns:
            Resolved Capability instance, or None if unavailable.
        """
        cap = self.registry.get(capability_id_or_alias)
        if not cap:
            logger.warning(f"Capability '{capability_id_or_alias}' not found in registry")
            return None

        # Check if disabled
        if not cap.enabled:
            logger.warning(f"Capability '{cap.capability_id}' is disabled")
            return None

        # Check experimental setting
        if cap.is_experimental and not self.config.enable_experimental:
            logger.warning(f"Experimental capability '{cap.capability_id}' disabled by configuration")
            return None

        # Deprecation handling & replacement redirect
        if cap.is_deprecated:
            logger.warning(f"Capability '{cap.capability_id}' is deprecated")
            if cap.replaced_by:
                replacement = self.registry.get(cap.replaced_by)
                if replacement and replacement.enabled:
                    logger.info(f"Redirecting deprecated capability '{cap.capability_id}' -> '{replacement.capability_id}'")
                    return replacement

        # Platform filter check
        if self.config.platform_filter:
            if self.config.platform_filter.lower() not in [p.lower() for p in cap.supported_platforms]:
                logger.warning(f"Capability '{cap.capability_id}' not supported on platform '{self.config.platform_filter}'")
                return None

        return cap
