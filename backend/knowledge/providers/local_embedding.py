import hashlib
from typing import List
from knowledge.providers.base import BaseEmbeddingProvider


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic local feature hashing embedding provider for offline / fallback search.
    """

    def __init__(self, vector_dim: int = 64):
        self.vector_dim = vector_dim

    def embed_text(self, text: str) -> List[float]:
        vec = [0.0] * self.vector_dim
        words = text.lower().split()
        if not words:
            return vec

        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.vector_dim
            vec[idx] += 1.0

        # L2 normalize
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]

        return vec
