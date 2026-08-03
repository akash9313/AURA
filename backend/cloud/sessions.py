import logging
import time
import uuid
from typing import Dict, Optional

logger = logging.getLogger("AURA.Cloud.Sessions")


class SessionManager:
    """Manages authentication tokens and session lifecycles."""

    def __init__(self):
        self.tokens: Dict[str, str] = {}  # token -> user_id

    def create_session(self, user_id: str) -> str:
        token = f"tok_{uuid.uuid4().hex}"
        self.tokens[token] = user_id
        logger.info(f"Created session token for user '{user_id}'")
        return token

    def verify_token(self, token: str) -> Optional[str]:
        return self.tokens.get(token)

    def revoke_session(self, token: str) -> bool:
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
