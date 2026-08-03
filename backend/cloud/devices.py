import logging
import time
import uuid
from typing import Dict, List, Optional
from cloud.models import DeviceSession

logger = logging.getLogger("AURA.Cloud.Devices")


class DeviceManager:
    """Manages registered devices, device revocation, and active device tracking."""

    def __init__(self):
        self.devices: Dict[str, DeviceSession] = {}

    def register_device(self, user_id: str, device_name: str, device_type: str = "desktop") -> DeviceSession:
        device_id = f"dev_{uuid.uuid4().hex[:8]}"
        session = DeviceSession(
            device_id=device_id,
            user_id=user_id,
            device_name=device_name,
            device_type=device_type,
            last_active=time.time()
        )
        self.devices[device_id] = session
        logger.info(f"Registered device '{device_name}' (ID: {device_id}) for user '{user_id}'")
        return session

    def revoke_device(self, device_id: str) -> bool:
        session = self.devices.get(device_id)
        if session:
            session.is_active = False
            logger.info(f"Revoked device '{device_id}'")
            return True
        return False

    def list_user_devices(self, user_id: str) -> List[DeviceSession]:
        return [dev for dev in self.devices.values() if dev.user_id == user_id and dev.is_active]
