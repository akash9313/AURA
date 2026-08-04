import logging
from typing import Any, Dict
from brain.streaming.models import TokenChunk

logger = logging.getLogger("AURA.Brain.Streaming.TokenStream")


class TokenStreamFormatter:
    """Formats TokenChunk objects into clean EventBus payload dicts."""

    def format_chunk(self, chunk: TokenChunk) -> Dict[str, Any]:
        return {
            "token": chunk.token,
            "token_index": chunk.token_index,
            "timestamp": chunk.timestamp,
            "is_first_token": chunk.is_first_token,
        }
