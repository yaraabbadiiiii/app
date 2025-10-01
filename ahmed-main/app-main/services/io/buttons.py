# io/buttons.py
import time

class Buttons:
    """
    يحاكي أزرار الجهاز (Capture, Next, Prev).
    يرسل أحداث عبر EventBus.
    """
    def __init__(self, bus):
        self.bus = bus
        self.last_press_time = 0
        self.double_press_threshold = 0.4  # نصف ثانية

    def press_capture(self, press_type="short"):
        """
        محاكاة كبسة زر Capture.
        """
        if press_type == "short":
            self.bus.emit("BTN_CAPTURE_SHORT")
        elif press_type == "long":
            self.bus.emit("BTN_CAPTURE_LONG")
        elif press_type == "double":
            now = time.time()
            if now - self.last_press_time <= self.double_press_threshold:
                self.bus.emit("BTN_CAPTURE_DOUBLE")
            self.last_press_time = now

    def press_next(self, press_type="short"):
        if press_type == "short":
            self.bus.emit("BTN_NEXT_SHORT")
        elif press_type == "long":
            self.bus.emit("BTN_NEXT_LONG")

    def press_prev(self, press_type="short"):
        if press_type == "short":
            self.bus.emit("BTN_PREV_SHORT")
        elif press_type == "long":
            self.bus.emit("BTN_PREV_LONG")
