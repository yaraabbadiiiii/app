# core/bus.py
from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback):
        self.subscribers[event_type].append(callback)

    def emit(self, event_type: str, data=None):
        print(f"[EventBus] Emitting event: {event_type} with data: {data}")
        for callback in self.subscribers[event_type]:
            callback(data)
