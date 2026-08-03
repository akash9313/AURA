import time
import unittest
from cloud.accounts import AccountManager
from cloud.auth import AuthenticationEngine
from cloud.backups import BackupManager
from cloud.conflicts import ConflictResolver
from cloud.devices import DeviceManager
from cloud.encryption import CloudEncryptionEngine
from cloud.models import ConflictPolicy, SyncPayload
from cloud.sessions import SessionManager
from cloud.sync import SyncEngine


class TestCloudPlatform(unittest.TestCase):

    def test_account_signup_signin(self):
        """Test account creation, sign in, and token verification."""
        acc_mgr = AccountManager()
        sess_mgr = SessionManager()
        auth = AuthenticationEngine(acc_mgr, sess_mgr)

        acc, token = auth.sign_up("user@example.com", "Password123!")
        self.assertEqual(acc.email, "user@example.com")
        self.assertEqual(auth.verify_session(token), acc.user_id)

        signed_acc, token2 = auth.sign_in("user@example.com", "Password123!")
        self.assertEqual(signed_acc.user_id, acc.user_id)

        with self.assertRaises(PermissionError):
            auth.sign_in("user@example.com", "WrongPassword")

    def test_device_manager(self):
        """Test device registration and revocation."""
        devices = DeviceManager()
        dev = devices.register_device("usr_1", "MacBook Pro", "laptop")
        self.assertTrue(dev.is_active)

        user_devs = devices.list_user_devices("usr_1")
        self.assertEqual(len(user_devs), 1)

        revoked = devices.revoke_device(dev.device_id)
        self.assertTrue(revoked)
        self.assertEqual(len(devices.list_user_devices("usr_1")), 0)

    def test_sync_and_conflict_resolution(self):
        """Test multi-device sync payload conflict resolution."""
        resolver = ConflictResolver()
        sync_engine = SyncEngine(conflict_resolver=resolver)

        p1 = SyncPayload(payload_id="p1", user_id="usr_1", device_id="dev_1", timestamp=100.0, preferences={"theme": "dark"})
        p2 = SyncPayload(payload_id="p2", user_id="usr_1", device_id="dev_2", timestamp=200.0, preferences={"theme": "light"})

        # Sync 1
        res1 = sync_engine.sync_device("usr_1", p1)
        self.assertEqual(res1.preferences["theme"], "dark")

        # Sync 2 -> Remote p2 timestamp (200.0) wins over p1 (100.0)
        res2 = sync_engine.sync_device("usr_1", p2, policy=ConflictPolicy.LAST_WRITE_WINS)
        self.assertEqual(res2.preferences["theme"], "light")

    def test_backups(self):
        """Test backup snapshot creation and restoration."""
        backups = BackupManager()
        snap = backups.create_backup("usr_1", {"workflows": ["wf_1"]})
        self.assertEqual(snap.user_id, "usr_1")

        restored = backups.restore_backup(snap.backup_id)
        self.assertIsNotNone(restored)
        self.assertIn("wf_1", restored.data["workflows"])

    def test_encryption(self):
        """Test CloudEncryptionEngine payload encryption/decryption."""
        enc = CloudEncryptionEngine()
        secret_msg = "Sensitive User Preferences"

        encrypted = enc.encrypt_data(secret_msg)
        self.assertTrue(encrypted.startswith("enc_"))

        decrypted = enc.decrypt_data(encrypted)
        self.assertEqual(decrypted, secret_msg)


if __name__ == "__main__":
    unittest.main()
