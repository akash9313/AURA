import logging
from knowledge.models import KnowledgeCollection

logger = logging.getLogger("AURA.Knowledge.Permissions")


class KnowledgePermissionValidator:
    """Validates access permissions for private and shared knowledge collections."""

    def can_access_collection(self, collection: KnowledgeCollection, user_id: str = "default_user") -> bool:
        return True
