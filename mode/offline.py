
from typing import List, Optional
from core import events as E

class OfflineOrchestrator:
    """
    Offline بسيط: يلتقط → يستقبل OCR_DONE(lines) → يقرأ السطر الحالي
    يفترض وجود:
      - bus: EventBus بنمطك الحالي (subscribe/emit)
      - tts: كائن يوفر speak(text) و stop()
      - session_store: يوفر save_state(dict) و load_state(default)
    """
    def __init__(self, bus, tts, session_store):
        self.bus = bus
        self.tts = tts
        self.session_store = session_store

        self.lines: List[str] = []
        self.line_index: int = 0
        self.paused: bool = False
        self._started: bool = False

    def name(self) -> str:
        return "offline"

    # ---------- lifecycle ----------
    def start(self):
        if self._started:
            return
        self._started = True

        # استرجاع آخر حالة
        state = self.session_store.load_state(default={"lineIndex": 0})
        self.line_index = int(state.get("lineIndex", 0))

        # اشتراكات للأزرار/الـOCR
        self.bus.subscribe(E.BTN_CAPTURE_SHORT, self._on_capture)
        self.bus.subscribe(E.BTN_NEXT_SHORT, self._on_next)
        self.bus.subscribe(E.BTN_PREV_SHORT, self._on_prev)
        self.bus.subscribe(E.BTN_NEXT_LONG, self._on_resume)
        self.bus.subscribe(E.BTN_PREV_LONG, self._on_pause)

        self.bus.subscribe(E.OCR_DONE, self._on_ocr_done)
        self.bus.subscribe(E.OCR_EMPTY, self._on_ocr_empty)

        # ممكن تعلن الحالة بالعربي
        # self._speak("الوضع أوفلاين جاهز")

    def stop(self):
        # تنظيف بسيط (اختياري)
        self._started = False
        try:
            self.tts.stop()
        except Exception:
            pass

    # ---------- events ----------
    def _on_capture(self, _data=None):
        if self.paused:
            return
        # هون بتعمل تريغر للالتقاط/الـOCR حسب نظامك
        # ممكن ترسل حدث للكاميرا أو للسيرفر؛ حالياً بس إعلان:
        # print("[Offline] capture requested")

    def _on_ocr_done(self, data):
        # توقع data: {"lines": List[str]}
        lines = (data or {}).get("lines") or []
        if not lines:
            return
        self.lines = lines
        self.line_index = min(self.line_index, len(self.lines) - 1) if self.lines else 0
        self._read_current_line()
        self._save_state()

    def _on_ocr_empty(self, _data=None):
        # self._speak("ما في نص مقروء")
        pass

    def _on_next(self, _data=None):
        if not self.lines or self.paused:
            return
        if self.line_index < len(self.lines) - 1:
            self.line_index += 1
            self._read_current_line()
            self._save_state()

    def _on_prev(self, _data=None):
        if not self.lines or self.paused:
            return
        if self.line_index > 0:
            self.line_index -= 1
            self._read_current_line()
            self._save_state()

    def _on_pause(self, _data=None):
        self.paused = True
        try:
            self.tts.stop()
        except Exception:
            pass
        # self._speak("توقفت القراءة")

    def _on_resume(self, _data=None):
        self.paused = False
        # self._speak("استئناف")
        self._read_current_line()

    # ---------- helpers ----------
    def _read_current_line(self):
        if not self.lines or self.paused:
            return
        line = self.lines[self.line_index]
        try:
            self.tts.speak(line)
        except Exception as e:
            print("[Offline] TTS error:", e)

    def _save_state(self):
        try:
            self.session_store.save_state({"mode": "Offline", "lineIndex": self.line_index})
        except Exception:
            pass

