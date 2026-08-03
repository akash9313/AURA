import logging
from core.events import Event
from core.service import Service
from cloud.accounts import AccountManager
from cloud.auth import AuthenticationEngine
from cloud.backups import BackupManager
from cloud.billing import BillingManager
from cloud.conflicts import ConflictResolver
from cloud.devices import DeviceManager
from cloud.encryption import CloudEncryptionEngine
from cloud.events import CloudEvent
from cloud.notifications import CloudNotificationManager
from cloud.quotas import QuotaManager
from cloud.sessions import SessionManager
from cloud.sync import SyncEngine

logger = logging.getLogger("AURA.Cloud.Service")


class CloudService(Service):
    """
    Cloud Platform Service wrapper connecting multi-device sync, authentication, and backups to EventBus.
    Remains strictly optional; AURA functions fully offline when cloud service is disabled.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.accounts = AccountManager()
        self.sessions = SessionManager()
        self.auth = AuthenticationEngine(self.accounts, self.sessions)
        self.devices = DeviceManager()
        self.encryption = CloudEncryptionEngine()
        self.conflicts = ConflictResolver()
        self.sync_engine = SyncEngine(conflict_resolver=self.conflicts)
        self.backups = BackupManager()
        self.notifications = CloudNotificationManager()
        self.quotas = QuotaManager()
        self.billing = BillingManager()
        self.enabled: bool = True

    def start(self):
        logger.info("Cloud Platform Service Started (Optional Cloud Features Active).")
        if self.bus:
            self.bus.subscribe(Event.GOAL_CREATED, self.on_goal_created)

    def on_goal_created(self, payload):
        goal = payload.get("goal", "").lower()
        if "sync" in goal or "backup" in goal:
            logger.info("Cloud Service processing sync/backup goal.")
