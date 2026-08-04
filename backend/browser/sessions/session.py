import logging
import time
from typing import Any, Dict, Optional
from browser.sessions.models import BrowserSessionData, BrowserSessionInfo, SessionState, SessionType
from browser.sessions.permissions import SessionPermissionManager
from browser.sessions.storage_state import StorageStateManager

logger = logging.getLogger("AURA.Browser.Sessions.Session")


class BrowserSession:
    """
    Active Browser Session Instance.
    Encapsulates session storage state, cookies, auth tokens, state lifecycle, and domain security permissions.
    Decoupled from Playwright.
    """

    def __init__(self, data: BrowserSessionData):
        self.data = data
        self.state: SessionState = SessionState.CREATED
        self.storage = StorageStateManager(initial_state=data.storage_state)
        self.permissions = SessionPermissionManager()
        self.state = SessionState.ACTIVE

    def touch(self) -> None:
        self.data.last_accessed_at = time.time()

    def get_info(self) -> BrowserSessionInfo:
        return BrowserSessionInfo(

            session_id=self.data.session_id,
            name=self.data.name,
            session_type=self.data.session_type,
            state=self.state,
            created_at=self.data.created_at,
            last_accessed_at=self.data.last_accessed_at,
            is_persistent=(self.data.session_type == SessionType.PERSISTENT),
        )

    def is_expired(self, timeout_seconds: float) -> bool:
        if self.data.session_type == SessionType.INCOGNITO:
            return False
        idle_time = time.time() - self.data.last_accessed_at
        return idle_time > timeout_seconds
