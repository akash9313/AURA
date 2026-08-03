from enum import Enum


class CloudEvent(Enum):
    """Event definitions for Cloud Platform."""
    USER_SIGNED_IN = "user_signed_in"
    USER_SIGNED_OUT = "user_signed_out"
    SYNC_STARTED = "sync_started"
    SYNC_COMPLETED = "sync_completed"
    DEVICE_REGISTERED = "device_registered"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
