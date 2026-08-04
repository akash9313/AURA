import logging
from typing import List
from api.models import APIKey, APIScope

logger = logging.getLogger("AURA.API.Permissions")


class ScopePermissionValidator:
    """Validates fine-grained API scope permissions."""

    def check_scope(self, api_key: APIKey, required_scope: APIScope) -> bool:
        if not api_key.is_active:
            logger.warning(f"API Key '{api_key.key_id}' is inactive.")
            return False

        has_scope = required_scope in api_key.scopes
        if not has_scope:
            logger.warning(f"Scope permission denied: Key '{api_key.key_id}' lacks scope '{required_scope.value}'")
        return has_scope
