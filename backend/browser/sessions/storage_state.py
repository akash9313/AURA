import logging
from typing import Any, Dict, Optional
from browser.sessions.cookies import CookieManager
from browser.sessions.models import StorageStateData

logger = logging.getLogger("AURA.Browser.Sessions.StorageState")


class StorageStateManager:
    """
    Manages Web Storage & Authentication Snapshots.
    Tracks localStorage, sessionStorage, and auth tokens while enforcing token masking.
    """

    def __init__(self, initial_state: Optional[StorageStateData] = None):
        self.state = initial_state or StorageStateData()
        self.cookie_manager = CookieManager()
        if self.state.cookies:
            for c in self.state.cookies:
                self.cookie_manager.add_cookie(c)

    def set_local_storage(self, origin: str, data: Dict[str, str]) -> None:
        self.state.local_storage[origin] = data

    def get_local_storage(self, origin: str) -> Dict[str, str]:
        return self.state.local_storage.get(origin, {})

    def set_session_storage(self, origin: str, data: Dict[str, str]) -> None:
        self.state.session_storage[origin] = data

    def set_auth_token(self, token_name: str, token_value: str) -> None:
        self.state.auth_tokens[token_name] = token_value
        logger.info(f"Auth token '{token_name}' stored securely.")

    def get_masked_auth_tokens(self) -> Dict[str, str]:
        return {k: f"***MASKED_{v[:3]}...***" if len(v) > 3 else "***MASKED***" for k, v in self.state.auth_tokens.items()}

    def capture_snapshot(self) -> StorageStateData:
        self.state.cookies = self.cookie_manager.export_all()
        return self.state

