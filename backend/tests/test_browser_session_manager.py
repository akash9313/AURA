import os
import shutil
import tempfile
import time
import unittest
from core.event_bus import EventBus
from browser.sessions.configuration import SessionConfig
from browser.sessions.cookies import CookieManager
from browser.sessions.events import SessionEvent
from browser.sessions.models import CookieData, SessionState, SessionType, StorageStateData
from browser.sessions.permissions import SessionPermissionManager
from browser.sessions.session import BrowserSession
from browser.sessions.session_manager import BrowserSessionManager
from browser.sessions.session_store import SessionStore
from browser.sessions.storage_state import StorageStateManager


class TestBrowserSessionManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="aura_test_sessions_")
        self.config = SessionConfig(persistence_path=self.temp_dir, session_timeout_seconds=0.5)
        self.bus = EventBus()
        self.manager = BrowserSessionManager(bus=self.bus, config=self.config)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cookie_manager_domain_filtering_and_expiration(self):
        """Test CookieManager domain filtering and expired cookie purging."""
        cm = CookieManager()
        c1 = CookieData(name="session_id", value="xyz123", domain="example.com")
        c2 = CookieData(name="expired_token", value="old", domain="example.com", expires=time.time() - 10.0)

        cm.add_cookie(c1)
        cm.add_cookie(c2)

        active_cookies = cm.get_cookies_for_domain("example.com")
        self.assertEqual(len(active_cookies), 1)
        self.assertEqual(active_cookies[0].name, "session_id")

        purged_count = cm.filter_expired()
        self.assertEqual(purged_count, 1)

    def test_storage_state_token_masking(self):
        """Test StorageStateManager secure token masking."""
        sm = StorageStateManager()
        sm.set_auth_token("bearer_token", "secret_jwt_token_value_12345")
        masked = sm.get_masked_auth_tokens()
        self.assertNotIn("secret_jwt_token_value_12345", masked["bearer_token"])
        self.assertIn("***MASKED", masked["bearer_token"])

    def test_session_store_persistence_and_corruption_recovery(self):
        """Test SessionStore disk persistence and corrupted session recovery."""
        store = SessionStore(config=self.config)
        info = self.manager.create_session("Test Session", SessionType.PERSISTENT)

        loaded = store.load_session(info.session_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Test Session")

        # Corrupt file
        filepath = store._get_filepath(info.session_id)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON CONTENT")

        recovered = store.load_session(info.session_id)
        self.assertIsNone(recovered)

    def test_session_permission_manager(self):
        """Test SessionPermissionManager domain access validation."""
        spm = SessionPermissionManager(allowed_domains=["github.com", "google.com"])
        self.assertTrue(spm.validate_access("https://github.com/aura"))
        self.assertFalse(spm.validate_access("https://malicious-site.org"))

    def test_session_manager_full_lifecycle_and_events(self):
        """Test BrowserSessionManager create, save, restore, switch, destroy, and events."""
        events = []
        self.bus.subscribe(SessionEvent.SESSION_CREATED.value, lambda p: events.append(p))
        self.bus.subscribe(SessionEvent.SESSION_SAVED.value, lambda p: events.append(p))

        s1 = self.manager.create_session("User Work Session", SessionType.PERSISTENT)
        self.assertIsNotNone(s1.session_id)

        saved = self.manager.save_session(s1.session_id)
        self.assertTrue(saved)

        restored = self.manager.restore_session(s1.session_id)
        self.assertIsNotNone(restored)

        switched = self.manager.switch_session(s1.session_id)
        self.assertEqual(switched.session_id, s1.session_id)

        destroyed = self.manager.destroy_session(s1.session_id)
        self.assertTrue(destroyed)
        self.assertEqual(len(self.manager.list_active_sessions()), 0)
        self.assertGreater(len(events), 0)


if __name__ == "__main__":
    unittest.main()
