import numpy as np


class Camera:
    def __init__(self, bus):
        self.bus = bus
        self._warm = False
        self._use_picam2 = False
        self._picam2 = None

        # Try PiCamera2 first
        try:
            from picamera2 import Picamera2  # type: ignore
            self._picam2 = Picamera2()
            self._picam2.configure(self._picam2.create_preview_configuration(main={"format": "RGB888"}))
            self._use_picam2 = True
        except Exception:
            self._use_picam2 = False

    def _ensure_started(self):
        if not self._warm and self._use_picam2 and self._picam2 is not None:
            self._picam2.start()
            self._warm = True

    def capture(self):
        self._ensure_started()
        self.bus.emit("CAMERA_SHOT_OK")

        if self._use_picam2 and self._picam2 is not None:
            frame = self._picam2.capture_array()
            # Picamera2 returns RGB888 already
            return frame

        # Fallback: return a dummy black frame
        return np.zeros((480, 640, 3), dtype=np.uint8)
