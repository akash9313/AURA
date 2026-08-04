import logging
import uuid
from typing import Dict, List, Optional
from api.models import APIKey, APIScope

logger = logging.getLogger("AURA.API.Auth")


class APIAuthenticator:
    """Manages API Key generation, verification, and revocation."""

    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}

    def create_api_key(self, name: str, scopes: List[APIScope]) -> APIKey:
        key_id = f"ak_{uuid.uuid4().hex[:8]}"
        secret_key = f"sk_{uuid.uuid4().hex}"
        api_key = APIKey(key_id=key_id, secret_key=secret_key, name=name, scopes=scopes)
        self.api_keys[secret_key] = api_key
        logger.info(f"Created API Key '{name}' (ID: {key_id}) with scopes {[s.value for s in scopes]}")
        return api_key

    def verify_key(self, secret_key: str) -> Optional[APIKey]:
        return self.api_keys.get(secret_key)
