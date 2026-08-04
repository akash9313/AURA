import logging
from typing import Any, Dict

logger = logging.getLogger("AURA.API.WebSocket")


class WebSocketHandler:
    """WebSocket & Server Sent Events (SSE) real-time streaming handler."""

    def stream_event(self, client_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        logger.info(f"WebSocket Stream [{client_id}] -> Event '{event_type}': {payload}")
