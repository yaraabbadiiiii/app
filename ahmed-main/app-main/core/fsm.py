from core.fsm import FSM, State
from core.bus import EventBus

class OfflineOrchestrator:
    """
    Orchestrator لوضع Offline.
    يتابع الأحداث من EventBus ويحول بين الحالات.
    """
    def __init__(self, bus: EventBus, tts, session_store):
        self.bus = bus
        self.fsm = FSM()
        self.tts = tts
        self.session_store = session_store
        self.lines = []
        self.line_index = 0

        # الاشتراك في الأحداث
        self.bus.subscribe("BTN_CAPTURE_SHORT", self.on_capture)
        self.bus.subscribe("OCR_DONE", self.on_ocr_done)
        self.bus.subscribe("OCR_EMPTY", self.on_ocr_empty)
        self.bus.subscribe("BTN_NEXT_SHORT", self.on_next)
        self.bus.subscribe("BTN_PREV_SHORT", self.on_prev)
        self.bus.subscribe("BTN_NEXT_LONG", self.on_resume)
        self.bus.subscribe("BTN_PREV_LONG", self.on_pause)

    def on_capture(self, _):
        self.fsm.transition(State.CAPTURING)
        print("[Offline] Capture triggered... (camera working)")

    def on_ocr_done(self, data):
        self.fsm.transition(State.READING_LOCAL)
        self.lines = data.get("lines", [])
        self.line_index = 0
        print(f"[Offline] OCR returned {len(self.lines)} lines.")
        self.read_current_line()

    def on_ocr_empty(self, _):
        self.fsm.transition(State.IDLE)
        self.tts.speak("No recognizable content found.")

    def on_next(self, _):
        if self.line_index < len(self.lines) - 1:
            self.line_index += 1
            self.read_current_line()

    def on_prev(self, _):
        if self.line_index > 0:
            self.line_index -= 1
            self.read_current_line()

    def on_resume(self, _):
        print("[Offline] Resuming auto-read mode...")
        while self.line_index < len(self.lines):
            self.read_current_line()
            self.line_index += 1

    def on_pause(self, _):
        self.fsm.transition(State.PAUSED)
        print("[Offline] Reading paused.")

    def read_current_line(self):
        if 0 <= self.line_index < len(self.lines):
            line = self.lines[self.line_index]
            self.tts.speak(line["text"])
            self.session_store.save_state({
                "mode": "Offline",
                "lineIndex": self.line_index
            })
