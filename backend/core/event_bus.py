from collections import defaultdict


class EventBus:

    def __init__(self):

        self.listeners = defaultdict(list)

    def subscribe(self, event, callback):

        self.listeners[event].append(callback)

    def publish(self, event, data=None):

        print(f"\n📢 EVENT -> {event.name}")

        for callback in self.listeners[event]:

            callback(data)