import csv
import io
import json
import logging
from typing import List
from monitoring.models import MetricRecord

logger = logging.getLogger("AURA.Monitoring.Exporter")


class MetricsExporter:
    """Metrics Exporter supporting JSON, CSV, and Prometheus text format."""

    def export_json(self, metrics: List[MetricRecord]) -> str:
        return json.dumps([m.to_dict() for m in metrics], indent=2)

    def export_csv(self, metrics: List[MetricRecord]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "name", "value", "unit", "tags"])
        for m in metrics:
            writer.writerow([m.timestamp, m.name, m.value, m.unit, json.dumps(m.tags)])
        return output.getvalue()

    def export_prometheus(self, metrics: List[MetricRecord]) -> str:
        lines = []
        for m in metrics:
            clean_name = m.name.replace(".", "_")
            tag_str = ",".join(f'{k}="{v}"' for k, v in m.tags.items())
            tags_formatted = f"{{{tag_str}}}" if tag_str else ""
            lines.append(f"# TYPE {clean_name} gauge")
            lines.append(f"{clean_name}{tags_formatted} {m.value}")
        return "\n".join(lines)
