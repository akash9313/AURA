from core.service import Service
from core.events import Event


class RuntimeService(Service):

    def start(self):
        print("Runtime Service Started")

    def stop(self):
        print("Runtime Service Stopped")