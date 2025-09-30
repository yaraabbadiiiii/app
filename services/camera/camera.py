# services/camera.py
class Camera:
    def __init__(self, bus):
        self.bus = bus
        self.first_capture = True

    def capture(self, has_text=True):
        self.bus.emit("CAMERA_SHOT_OK")

        if self.first_capture:
            self.first_capture = False
            qr_frame = {"type": "QR", "data": "sample_qr_code"}
            return qr_frame

        if has_text:
            lines = [
                {"id": "l_001", "text": "مرحبا بك في الجهاز", "lang": "ar"},
                {"id": "l_002", "text": "This is a test", "lang": "en"},
            ]
            self.bus.emit("OCR_DONE", {"lines": lines})
            return lines
        else:
            self.bus.emit("OCR_EMPTY")
            return None
