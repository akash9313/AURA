import logging
import uuid
from typing import Dict
from browser.models import BrowserSession

logger = logging.getLogger("AURA.Browser.Sessions")


class BrowserSessionManager:
    """
    Manager responsible for browser profile contexts, incognito mode, and persistent sessions.
    """

    def __init__(self):
        self._sessions: Dict[str, BrowserSession] = {}
        self._active_session_id: str = "default"
        self._sessions["default"] = BrowserSession(session_id="default")

    def create_session(self, incognito: bool = False) -> BrowserSession:
        sid = f"sess_{str(uuid.uuid4())[:8]}"
        sess = BrowserSession(session_id=sid, is_incognito=incognito)
        self._sessions[sid] = sess
        self._active_session_id = sid
        return sess

    def get_active_session(self) -> BrowserSession:
        return self._sessions.get(self._active_session_id, self._sessions["default"])
