import time
import unittest
from core.events import Event
from core.event_bus import EventBus
from monitoring.configuration import MonitoringConfig
from monitoring.dashboard import LocalDashboardRenderer
from monitoring.exporter import MetricsExporter
from monitoring.health import HealthChecker
from monitoring.logger import StructuredLogger
from monitoring.metrics import MetricsCollector
from monitoring.models import HealthStatus
from monitoring.profiler import PerformanceProfiler
from monitoring.service import MonitoringService
from monitoring.tracer import PipelineTracer


class TestMonitoringTelemetry(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.config = MonitoringConfig()
        self.collector = MetricsCollector(config=self.config)
        self.tracer = PipelineTracer()
        self.profiler = PerformanceProfiler()
        self.logger = StructuredLogger()
        self.health_checker = HealthChecker()
        self.exporter = MetricsExporter()
        self.dashboard = LocalDashboardRenderer()
        self.service = MonitoringService(bus=self.bus, config=self.config)

    def tearDown(self):
        self.service.stop()

    def test_metrics_collector(self):
        """Test recording metrics and collecting system CPU/RAM usage."""
        m1 = self.collector.record_metric("stt_latency", 120.0, "ms", tags={"model": "whisper"})
        self.assertEqual(m1.name, "stt_latency")
        self.assertEqual(m1.value, 120.0)

        sys_metrics = self.collector.collect_system_metrics()
        self.assertIn("cpu_percent", sys_metrics)
        self.assertIn("ram_percent", sys_metrics)
        self.assertIn("thread_count", sys_metrics)

    def test_pipeline_tracer(self):
        """Test start span, finish span, and duration measurement."""
        span = self.tracer.start_span("llm_generation")
        time.sleep(0.01)
        finished_span = self.tracer.finish_span(span.span_id)

        self.assertIsNotNone(finished_span)
        self.assertGreater(finished_span.duration_ms, 0.0)

    def test_performance_profiler(self):
        """Test process profiling."""
        prof = self.profiler.profile_process()
        self.assertIn("rss_bytes", prof)
        self.assertIn("num_threads", prof)

    def test_structured_logger(self):
        """Test JSON structured logging format."""
        log_json = self.logger.log_event("STT", "Transcription complete", correlation_id="corr_123", duration_ms=45.0)
        self.assertIn('"component": "STT"', log_json)
        self.assertIn('"correlation_id": "corr_123"', log_json)

    def test_health_checker(self):
        """Test health check status report."""
        status = self.health_checker.check_health()
        self.assertIn(status.status, (HealthStatus.HEALTHY, HealthStatus.WARNING))
        self.assertIn("speech", status.services)

    def test_metrics_exporter(self):
        """Test JSON, CSV, and Prometheus format exports."""
        self.collector.record_metric("test_metric", 42.0, "ms")
        metrics = self.collector.get_recent_metrics()

        json_out = self.exporter.export_json(metrics)
        self.assertIn('"name": "test_metric"', json_out)

        csv_out = self.exporter.export_csv(metrics)
        self.assertIn("test_metric", csv_out)

        prom_out = self.exporter.export_prometheus(metrics)
        self.assertIn("test_metric 42.0", prom_out)

    def test_local_dashboard_renderer(self):
        """Test dashboard rendering."""
        self.collector.record_metric("llm_latency", 250.0, "ms")
        health = self.health_checker.check_health()
        metrics = self.collector.get_recent_metrics()

        dash_text = self.dashboard.render_summary(metrics, health)
        self.assertIn("AURA PERFORMANCE TELEMETRY DASHBOARD", dash_text)
        self.assertIn(health.status.value.upper(), dash_text)


    def test_monitoring_service_passive_observation(self):
        """Test MonitoringService passive event observation."""
        self.service.start()
        self.bus.publish(Event.FINAL_TRANSCRIPT, {"inference_time_ms": 115.0})
        self.bus.publish(Event.STREAMING_RESPONSE, {"is_first_token": True, "first_token_latency_ms": 320.0})
        self.bus.publish(Event.SPEECH_INTERRUPTED, {})

        time.sleep(0.05)
        recent = self.service.metrics_collector.get_recent_metrics()
        metric_names = [m.name for m in recent]
        self.assertIn("stt.inference_time_ms", metric_names)
        self.assertIn("llm.first_token_latency_ms", metric_names)


if __name__ == "__main__":
    unittest.main()
