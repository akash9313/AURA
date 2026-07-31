from core.service import Service
from core.events import Event


class MemoryService(Service):

    def __init__(self, bus, store):

        self.bus = bus

        self.store = store

    def start(self):

        print("Memory Service Started")

        self.bus.subscribe(
            Event.MEMORY_SAVE,
            self.save_memory
        )

        self.bus.subscribe(
            Event.MEMORY_GET,
            self.get_memory
        )

    def stop(self):

        print("Memory Service Stopped")

    def save_memory(self, data):

        self.store.save(
            data["key"],
            data["value"]
        )

    def get_memory(self, key):

        value = self.store.get(key)

        print(value)