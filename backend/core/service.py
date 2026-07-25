from abc import ABC

class Service(ABC):
    def __init__(self, bus):
        self.bus = bus

    def initialize(self):
        """Register events and prepare resources."""
        pass

    def start(self):
        """Start the service."""
        pass

    def stop(self):
        """Clean up resources."""
        pass