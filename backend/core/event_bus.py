from collections import defaultdict


# High-frequency events that should not flood console output
_SUPPRESSED_EVENTS = {
    "AUDIO_CHUNK", "silence_detected", "MIC_STARTED",
}


class EventBus:

    def __init__(self):

        self.listeners = defaultdict(list)

    def subscribe(self, event, callback):

        self.listeners[event].append(callback)

    def publish(self, event, data=None):

        event_name = event.name if hasattr(event, "name") else str(event)

        if event_name not in _SUPPRESSED_EVENTS:
            print(f"[EVENT] -> {event_name}")

        for callback in self.listeners[event]:

            callback(data)