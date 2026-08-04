import logging
import threading
import time
from typing import Optional
from core.events import Event
from core.service import Service
from monitoring.configuration import MonitoringConfig
from monitoring.dashboard import LocalDashboardRenderer
from monitoring.exporter import MetricsExporter
from monitoring.health import HealthChecker
from monitoring.logger import StructuredLogger
from monitoring.metrics import MetricsCollector
from monitoring.profiler import PerformanceProfiler
from monitoring.tracer import PipelineTracer

logger = logging.getLogger("AURA.Monitoring.Service")


class MonitoringService(Service):
    """
    Passive Observability & Performance Telemetry Service.
    Subscribes to all EventBus events, records latencies, profiles system usage, and manages health checks.
    """

    def __init__(self, bus, config: Optional[MonitoringConfig] = None):
        super().__init__(bus)
        self.config = config or MonitoringConfig()
        self.metrics_collector = MetricsCollector(config=self.config)
        self.tracer = PipelineTracer()
        self.profiler = PerformanceProfiler()
        self.structured_logger = StructuredLogger()
        self.health_checker = HealthChecker()
        self.exporter = MetricsExporter()
        self.dashboard = LocalDashboardRenderer()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self):
        logger.info("Observability & Performance Telemetry Service Started.")
        if self.bus:
            # Subscribe passively to pipeline events
            self.bus.subscribe(Event.VOICE_STARTED, self.on_voice_started)
            self.bus.subscribe(Event.FINAL_TRANSCRIPT, self.on_final_transcript)
            self.bus.subscribe(Event.STREAMING_RESPONSE, self.on_streaming_response)
            self.bus.subscribe(Event.AI_RESPONSE_READY, self.on_ai_response_ready)
            self.bus.subscribe(Event.SPEECH_STARTED, self.on_speech_started)
            self.bus.subscribe(Event.SPEECH_COMPLETED, self.on_speech_completed)
            self.bus.subscribe(Event.SPEECH_INTERRUPTED, self.on_speech_interrupted)

        self._stop_event.clear()
        self._monitoring_thread = threading.Thread(target=self._periodic_collection_loop, daemon=True)
        self._monitoring_thread.start()

    def stop(self):
        logger.info("Observability & Performance Telemetry Service Stopped.")
        self._stop_event.set()

    def on_voice_started(self, payload: dict):
        self.tracer.start_span("voice_activity_detection")

    def on_final_transcript(self, payload: dict):
        if isinstance(payload, dict):
            inf_time = payload.get("inference_time_ms", 0.0)
            self.metrics_collector.record_metric("stt.inference_time_ms", inf_time, "ms")

    def on_streaming_response(self, payload: dict):
        if isinstance(payload, dict) and payload.get("is_first_token"):
            latency = payload.get("first_token_latency_ms", 50.0)
            self.metrics_collector.record_metric("llm.first_token_latency_ms", latency, "ms")

    def on_ai_response_ready(self, payload: dict):
        pass

    def on_speech_started(self, payload: dict):
        pass

    def on_speech_completed(self, payload: dict):
        pass

    def on_speech_interrupted(self, payload: dict):
        self.metrics_collector.record_metric("conversation.interruption_count", 1.0, "count")

    def _periodic_collection_loop(self):
        while not self._stop_event.is_set():
            try:
                self.metrics_collector.collect_system_metrics()
                health = self.health_checker.check_health()
                if health.warnings and self.bus:
                    self.bus.publish("health_warning", health.to_dict())
            except Exception as e:
                logger.error(f"Error in periodic monitoring loop: {e}")

            time.sleep(self.config.collection_interval_seconds)
