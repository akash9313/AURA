import logging
import uuid
from typing import Dict, List, Optional
from knowledge.models import KnowledgeCollection

logger = logging.getLogger("AURA.Knowledge.Collections")


class CollectionManager:
    """
    Manages Knowledge Collections (Projects, Courses, Research Topics, Books, Work, Personal).
    """

    def __init__(self):
        self.collections: Dict[str, KnowledgeCollection] = {}
        self._create_default_collections()

    def _create_default_collections(self):
        defaults = ["Projects", "Courses", "Research Topics", "Books", "Work", "Personal"]
        for d in defaults:
            cid = d.lower().replace(" ", "_")
            self.collections[cid] = KnowledgeCollection(collection_id=cid, name=d, description=f"{d} collection")

    def create_collection(self, name: str, description: str, tags: Optional[List[str]] = None) -> KnowledgeCollection:
        cid = f"col_{uuid.uuid4().hex[:8]}"
        col = KnowledgeCollection(collection_id=cid, name=name, description=description, tags=tags or [])
        self.collections[cid] = col
        logger.info(f"Created Knowledge Collection '{name}' (ID: {cid})")
        return col

    def get_collection(self, collection_id: str) -> Optional[KnowledgeCollection]:
        return self.collections.get(collection_id)
