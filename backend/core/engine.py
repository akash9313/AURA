from core.event_bus import EventBus
from core.service import Service


class AuraEngine:

    def __init__(self):
        self.services = {}
        self.bus = EventBus()

    def register(self, name: str, service: Service):
        self.services[name] = service
        print(f"Registered service: {name}")

    def start(self):
        print("Starting AuraEngine...")
        for name, service in self.services.items():
            service.start()

    def stop(self):
        print("Stopping AuraEngine...")
        for name, service in self.services.items():
            service.stop()