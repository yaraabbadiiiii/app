# camera/camera.py
class Camera:
    """
    محاكاة الكاميرا.
    عند التصوير، تبعث EVENT CAMERA_SHOT_OK.
    """
    def __init__(self, bus):
        self.bus = bus

    def capture(self, has_text=True):
        """
        يحاكي التقاط صورة.
        - إذا فيها نص → يبعث OCR_DONE.
        - إذا فاضية → يبعث OCR_EMPTY.
        """
        self.bus.emit("CAMERA_SHOT_OK")
        if has_text:
            lines = [
                {"id": "l_001", "text": "مرحبا بك في الجهاز", "lang": "ar"},
                {"id": "l_002", "text": "This is a test", "lang": "en"},
            ]
            self.bus.emit("OCR_DONE", {"lines": lines})
        else:
            self.bus.emit("OCR_EMPTY")
