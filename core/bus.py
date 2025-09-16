# core/bus.py
from collections import defaultdict

class EventBus:
    """
    EventBus مسؤول عن تمرير الأحداث بين الخدمات (Buttons, Camera, OCR, Orchestrator...).
    """
    def _init_(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback):
        """
        يضيف مستمع (subscriber) لحدث معين.
        """
        self.subscribers[event_type].append(callback)

    def emit(self, event_type: str, data=None):
        """
        ينشر حدث ويرسله لكل المستمعين.
        """
        print(f"[EventBus] Emitting event: {event_type} with data: {data}")
        for callback in self.subscribers[event_type]:
            callback(data)
