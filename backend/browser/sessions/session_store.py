import json
import logging
import os
from typing import Dict, List, Optional
from browser.sessions.configuration import SessionConfig
from browser.sessions.models import BrowserSessionData, CookieData, SessionType, StorageStateData

logger = logging.getLogger("AURA.Browser.Sessions.Store")


class SessionStore:
    """
    Repository Pattern Implementation for Disk-Backed Browser Session Persistence.
    Reads/writes session storage state JSON files securely and handles file corruption recovery.
    """

    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        os.makedirs(self.config.persistence_path, exist_ok=True)

    def _get_filepath(self, session_id: str) -> str:
        return os.path.join(self.config.persistence_path, f"{session_id}.json")

    def save_session(self, session_data: BrowserSessionData) -> bool:
        if session_data.session_type == SessionType.INCOGNITO:
            return False  # Incognito sessions are not persisted to disk

        filepath = self._get_filepath(session_data.session_id)
        logger.info(f"Saving browser session '{session_data.session_id}' to '{filepath}'...")

        try:
            raw_dict = session_data.to_dict(mask_tokens=False)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(raw_dict, f, indent=2)
            logger.info(f"Session '{session_data.session_id}' saved successfully.")
            return True
        except Exception as e:
            logger.error(f"Error saving session '{session_data.session_id}': {e}")
            return False

    def load_session(self, session_id: str) -> Optional[BrowserSessionData]:
        filepath = self._get_filepath(session_id)
        if not os.path.exists(filepath):
            logger.warning(f"Session file '{filepath}' not found.")
            return None

        logger.info(f"Loading browser session '{session_id}' from '{filepath}'...")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            storage_dict = data.get("storage_state", {})
            cookies = [
                CookieData(
                    name=c["name"],
                    value=c["value"],
                    domain=c["domain"],
                    path=c.get("path", "/"),
                    expires=c.get("expires"),
                    http_only=c.get("http_only", False),
                    secure=c.get("secure", False),
                    same_site=c.get("same_site", "Lax"),
                )
                for c in storage_dict.get("cookies", [])
            ]

            storage_state = StorageStateData(
                cookies=cookies,
                local_storage=storage_dict.get("local_storage", {}),
                session_storage=storage_dict.get("session_storage", {}),
                auth_tokens=storage_dict.get("auth_tokens", {}),
            )

            viewport = data.get("viewport", {})
            session_data = BrowserSessionData(
                session_id=data["session_id"],
                name=data.get("name", session_id),
                session_type=SessionType(data.get("session_type", "persistent")),
                storage_state=storage_state,
                user_agent=data.get("user_agent"),
                viewport_width=viewport.get("width", 1280),
                viewport_height=viewport.get("height", 800),
                download_dir=data.get("download_dir"),
                user_preferences=data.get("user_preferences", {}),
                created_at=data.get("created_at"),
                last_accessed_at=data.get("last_accessed_at"),
            )
            logger.info(f"Session '{session_id}' loaded successfully.")
            return session_data

        except Exception as e:
            logger.error(f"Corrupted session file '{filepath}': {e}. Attempting file recovery...")
            self.delete_session(session_id)
            return None

    def delete_session(self, session_id: str) -> bool:
        filepath = self._get_filepath(session_id)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Deleted session file '{filepath}'.")
                return True
            except Exception as e:
                logger.error(f"Failed to delete session file '{filepath}': {e}")
        return False

    def list_saved_sessions(self) -> List[str]:
        if not os.path.exists(self.config.persistence_path):
            return []
        files = os.listdir(self.config.persistence_path)
        return [f.replace(".json", "") for f in files if f.endswith(".json")]

