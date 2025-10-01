from core.bus import EventBus
from core import events as E
from services.audio.beep_service import BeepService
from session.session_store import SessionStore as RealSessionStore
from mode.offline import OfflineOrchestrator


class InMemorySessionStore:
    def __init__(self):
        self.state = {}
    def save_state(self, s):
        self.state = dict(s)
    def load_state(self, default=None):
        return dict(self.state) if self.state else (default or {})


def test_offline_read_single_line():
    bus = EventBus()
    tts = BeepService()
    store = InMemorySessionStore()
    offline = OfflineOrchestrator(bus, tts, store)
    offline.start()

    lines = ["hello", "world"]
    bus.emit(E.OCR_DONE, {"lines": lines})

    assert store.state.get("mode") == "Offline"
    assert store.state.get("lineIndex") == 0

