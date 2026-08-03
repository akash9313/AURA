import logging
from typing import List, Optional
from knowledge.providers.base import BaseEmbeddingProvider
from knowledge.providers.local_embedding import LocalEmbeddingProvider

logger = logging.getLogger("AURA.Knowledge.CloudEmbedding")


class CloudEmbeddingProvider(BaseEmbeddingProvider):
    """
    Cloud embedding provider wrapper with fallback to local embedding provider.
    """

    def __init__(self, fallback_provider: Optional[BaseEmbeddingProvider] = None):
        self.fallback = fallback_provider if fallback_provider is not None else LocalEmbeddingProvider()

    def embed_text(self, text: str) -> List[float]:
        try:
            # Cloud API embedding call placeholder -> fallback to local vector
            return self.fallback.embed_text(text)
        except Exception as e:
            logger.warning(f"Cloud embedding failed, falling back to local: {e}")
            return self.fallback.embed_text(text)
