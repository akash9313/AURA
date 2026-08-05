"""
Mission Embedding Engine.
Generates text embedding vectors and computes cosine similarity scores for semantic experience search.
"""

import math
import zlib
from typing import List


class MissionEmbeddingEngine:
    """
    Computes vector embeddings and similarity metrics.
    """

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate lightweight deterministic embedding vector for text.

        Returns:
            List of floats representing a 64-dimensional normalized vector.
        """
        if not text:
            return [0.0] * 64

        words = text.lower().split()
        vec = [0.0] * 64

        for word in words:
            # Deterministic CRC32 hashing
            h = zlib.crc32(word.encode("utf-8"))
            idx1 = h % 64
            idx2 = (h >> 5) % 64
            vec[idx1] += 1.0
            vec[idx2] += 0.5

        # Also add character n-gram hashing
        for i in range(len(text) - 2):
            ngram = text[i : i + 3].lower()
            h_ng = zlib.crc32(ngram.encode("utf-8")) % 64
            vec[h_ng] += 0.25

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 4) for v in vec]
        return vec

    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """
        Compute cosine similarity between two embedding vectors.

        Returns:
            Cosine similarity score between 0.0 and 1.0.
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        score = dot_product / (norm_a * norm_b)
        return round(max(0.0, min(1.0, score)), 4)
