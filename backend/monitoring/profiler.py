import logging
import psutil
import time
from typing import Dict, Any

logger = logging.getLogger("AURA.Monitoring.Profiler")


class PerformanceProfiler:
    """Lightweight Performance and Resource Profiler."""

    def profile_process(self) -> Dict[str, Any]:
        process = psutil.Process()
        with process.oneshot():
            cpu_times = process.cpu_times()
            mem_info = process.memory_info()
            num_threads = process.num_threads()

        return {
            "user_cpu_time_s": cpu_times.user,
            "system_cpu_time_s": cpu_times.system,
            "rss_bytes": mem_info.rss,
            "vms_bytes": mem_info.vms,
            "num_threads": num_threads,
            "timestamp": time.time()
        }
