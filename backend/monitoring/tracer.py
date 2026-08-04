import logging
import uuid
from typing import Dict, Optional
from monitoring.models import TraceSpan

logger = logging.getLogger("AURA.Monitoring.Tracer")


class PipelineTracer:
    """
    End-to-End Pipeline Tracer.
    Measures component trace spans with correlation IDs across the conversational execution pipeline.
    """

    def __init__(self):
        self.active_spans: Dict[str, TraceSpan] = {}

    def start_span(self, name: str, trace_id: Optional[str] = None, tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        t_id = trace_id or f"tr_{uuid.uuid4().hex[:8]}"
        s_id = f"sp_{uuid.uuid4().hex[:8]}"

        span = TraceSpan(
            trace_id=t_id,
            span_id=s_id,
            name=name,
            tags=tags or {}
        )
        self.active_spans[s_id] = span
        logger.debug(f"Trace Span Started: '{name}' (Trace ID: '{t_id}')")
        return span

    def finish_span(self, span_id: str) -> Optional[TraceSpan]:
        span = self.active_spans.pop(span_id, None)
        if span:
            span.finish()
            logger.debug(f"Trace Span Finished: '{span.name}' in {span.duration_ms:.2f}ms")
        return span
