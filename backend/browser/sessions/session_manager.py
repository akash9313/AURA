import logging
import time
from typing import Any, Dict, List, Optional
from browser.sessions.configuration import SessionConfig
from browser.sessions.events import SessionEvent
from browser.sessions.models import (
    BrowserSessionData,
    BrowserSessionInfo,
    SessionHealthStatus,
    SessionState,
    SessionType,
)
from browser.sessions.session import BrowserSession
from browser.sessions.session_store import SessionStore

logger = logging.getLogger("AURA.Browser.Sessions.Manager")


class BrowserSessionManager:
    """
    Production-Grade Browser Session Manager.
    Controls browser session lifecycle, storage state persistence, multi-session isolation, and timeout enforcement.
    Independent of Playwright or any specific automation provider.
    """

    def __init__(self, bus=None, config: Optional[SessionConfig] = None):
        self.bus = bus
        self.config = config or SessionConfig()
        self.store = SessionStore(config=self.config)
        self._active_sessions: Dict[str, BrowserSession] = {}
        self.active_session_id: Optional[str] = None

    def create_session(
        self,
        name: str,
        session_type: SessionType = SessionType.PERSISTENT,
        user_agent: Optional[str] = None,
        viewport_width: int = 1280,
        viewport_height: int = 800,
    ) -> BrowserSessionInfo:
        session_id = f"session_{len(self._active_sessions) + 1}_{int(time.time())}"
        data = BrowserSessionData(
            session_id=session_id,
            name=name,
            session_type=session_type,
            user_agent=user_agent,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
        )

        session = BrowserSession(data=data)
        self._active_sessions[session_id] = session
        self.active_session_id = session_id

        if session_type == SessionType.PERSISTENT:
            self.store.save_session(data)

        info = session.get_info()
        logger.info(f"Session '{session_id}' ('{name}') created successfully (Type={session_type.value}).")

        if self.bus:
            self.bus.publish(SessionEvent.SESSION_CREATED.value, info.to_dict())

        return info

    def restore_session(self, session_id: str) -> Optional[BrowserSessionInfo]:
        if session_id in self._active_sessions:
            session = self._active_sessions[session_id]
            session.touch()
            return session.get_info()

        data = self.store.load_session(session_id)
        if not data:
            logger.warning(f"Could not restore session '{session_id}'. File missing or corrupted.")
            return None

        session = BrowserSession(data=data)
        session.state = SessionState.ACTIVE
        self._active_sessions[session_id] = session
        self.active_session_id = session_id

        info = session.get_info()
        logger.info(f"Session '{session_id}' restored from persistent store.")

        if self.bus:
            self.bus.publish(SessionEvent.SESSION_RESTORED.value, info.to_dict())

        return info

    def save_session(self, session_id: str) -> bool:
        session = self._active_sessions.get(session_id)
        if not session:
            return False

        session.data.storage_state = session.storage.capture_snapshot()
        saved = self.store.save_session(session.data)

        if saved:
            session.state = SessionState.SAVED
            if self.bus:
                self.bus.publish(SessionEvent.SESSION_SAVED.value, session.get_info().to_dict())

        return saved

    def switch_session(self, session_id: str) -> Optional[BrowserSessionInfo]:
        session = self._active_sessions.get(session_id)
        if not session:
            info = self.restore_session(session_id)
            if not info:
                return None
            return info

        session.touch()
        self.active_session_id = session_id
        logger.info(f"Switched active session to '{session_id}'.")
        return session.get_info()

    def destroy_session(self, session_id: str) -> bool:
        session = self._active_sessions.pop(session_id, None)
        if not session:
            return False

        session.state = SessionState.DESTROYED
        if session.data.session_type == SessionType.PERSISTENT:
            self.store.delete_session(session_id)

        if self.active_session_id == session_id:
            self.active_session_id = list(self._active_sessions.keys())[0] if self._active_sessions else None

        logger.info(f"Session '{session_id}' destroyed.")

        if self.bus:
            self.bus.publish(SessionEvent.SESSION_DESTROYED.value, {"session_id": session_id})

        return True

    def list_active_sessions(self) -> List[BrowserSessionInfo]:
        return [s.get_info() for s in self._active_sessions.values()]

    def cleanup_expired_sessions(self) -> int:
        expired: List[str] = []
        for sid, session in self._active_sessions.items():
            if session.is_expired(self.config.session_timeout_seconds):
                expired.append(sid)

        for sid in expired:
            session = self._active_sessions.get(sid)
            if session:
                session.state = SessionState.EXPIRED
                if self.bus:
                    self.bus.publish(SessionEvent.SESSION_EXPIRED.value, {"session_id": sid})
                self.destroy_session(sid)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions.")

        return len(expired)

    def get_health_status(self) -> SessionHealthStatus:
        active_count = len(self._active_sessions)
        persistent_count = sum(1 for s in self._active_sessions.values() if s.data.session_type == SessionType.PERSISTENT)

        return SessionHealthStatus(
            active_sessions_count=active_count,
            persistent_sessions_count=persistent_count,
            expired_sessions_count=0,
            total_storage_mb=len(self.store.list_saved_sessions()) * 0.05,
        )

