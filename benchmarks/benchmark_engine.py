import os
import sys
import time
import tempfile

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from core.event_bus import EventBus
from core.events import Event
from memory.persistence import SQLiteDatabase
from memory.store import SQLiteMemoryRepository
from memory.manager import MemoryManager
from tools.registry import ToolRegistry
from cognition.engine import CognitiveEngine

def benchmark_event_bus(iterations: int = 10000) -> float:
    """Benchmark EventBus publish/subscribe throughput."""
    bus = EventBus()
    count = 0
    def handler(data):
        nonlocal count
        count += 1

    bus.subscribe("benchmark_event", handler)
    start = time.time()
    for _ in range(iterations):
        bus.publish("benchmark_event", {"val": 1})
    elapsed = time.time() - start
    rate = iterations / elapsed
    print(f"[BENCHMARK] EventBus Throughput: {rate:,.0f} events/sec ({elapsed*1000:.2f} ms for {iterations:,} events)")
    return rate

def benchmark_memory_retrieval(iterations: int = 100) -> float:
    """Benchmark Memory Engine retrieval latency."""
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    
    db = SQLiteDatabase(db_path=temp_db.name)
    repo = SQLiteMemoryRepository(db=db)
    mem = MemoryManager(repo=repo)

    start = time.time()
    for i in range(iterations):
        mem.working.set_variable(f"key_{i}", f"val_{i}")
        _ = mem.working.get_variable(f"key_{i}")
    elapsed = time.time() - start
    avg_latency = (elapsed / iterations) * 1000

    if os.path.exists(temp_db.name):
        os.remove(temp_db.name)

    print(f"[BENCHMARK] Memory Retrieval Latency: {avg_latency:.3f} ms/query")
    return avg_latency

def benchmark_tool_registry() -> float:
    """Benchmark ToolRegistry auto-discovery latency."""
    start = time.time()
    registry = ToolRegistry(auto_discover=True)
    elapsed = time.time() - start
    tools_count = len(registry.list_tools())
    print(f"[BENCHMARK] ToolRegistry Discovery: {elapsed*1000:.2f} ms ({tools_count} tools registered)")
    return elapsed

def main():
    print("==================================================")
    print("AURA AI OS Performance & Benchmark Suite")
    print("==================================================\n")
    
    benchmark_event_bus(iterations=10000)
    benchmark_memory_retrieval(iterations=100)
    benchmark_tool_registry()

    print("\n[SUCCESS] Benchmark Suite Execution Completed Cleanly!")


if __name__ == "__main__":
    main()
