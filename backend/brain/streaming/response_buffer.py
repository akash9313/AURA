import logging
import time
from typing import List, Optional
from brain.streaming.models import StreamingResponsePayload, TokenChunk

logger = logging.getLogger("AURA.Brain.Streaming.ResponseBuffer")


class StreamingResponseBuffer:
    """
    Accumulates streaming token chunks into complete responses and calculates streaming metrics.
    """

    def __init__(self):
        self.tokens: List[TokenChunk] = []
        self.start_time: Optional[float] = None
        self.first_token_time: Optional[float] = None

    def start_session(self) -> None:
        self.tokens.clear()
        self.start_time = time.time()
        self.first_token_time = None

    def add_token(self, token_str: str) -> TokenChunk:
        now = time.time()
        is_first = (self.first_token_time is None)
        if is_first:
            self.first_token_time = now

        chunk = TokenChunk(
            token=token_str,
            token_index=len(self.tokens) + 1,
            timestamp=now,
            is_first_token=is_first
        )
        self.tokens.append(chunk)
        return chunk

    def get_full_text(self) -> str:
        return "".join(t.token for t in self.tokens)


    def get_payload(self, finish_reason: str = "completed") -> StreamingResponsePayload:
        now = time.time()
        t0 = self.start_time or now
        t_first = self.first_token_time or now
        first_token_latency = (t_first - t0) * 1000.0
        total_dur = (now - t0) * 1000.0

        return StreamingResponsePayload(
            full_text=self.get_full_text(),
            total_tokens=len(self.tokens),
            first_token_latency_ms=first_token_latency,
            total_duration_ms=total_dur,
            finish_reason=finish_reason
        )
