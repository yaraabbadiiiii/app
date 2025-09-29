import logging
from core.bus import EventBus
from core.config import APP_NAME
from core.events import BTN_CAPTURE_SHORT
from core.storge import SessionStore
from mode.mode_manger import ModeManager
from services.audio import BeepService
from services.camera import CameraService
from services.vision import VisionService
from connectivity.network import handle_frame

from offline import OfflineOrchestrator
from online import OnlineOrchestrator  # placeholder مؤقت للأونلاين مود

def main():
    # 1. تهيئة الـ logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(APP_NAME)
    logger.info("Starting AI Reader System")

    # 2. إنشاء EventBus
    bus = EventBus()

    # 3. تحميل SessionStore
    session_store = SessionStore()

    # 4. Mode Manager
    mode_manager = ModeManager()

    # 5. تجهيز الخدمات الأساسية
    camera = CameraService(bus)
    vision = VisionService(bus)
    audio = BeepService(bus)

    # ----------- تحديد المود عن طريق QR ----------
    logger.info("Checking network mode via QR...")
    first_frame = camera.capture_frame()

    if first_frame is not None:
        qr_result = handle_frame(first_frame)
        if qr_result and qr_result.get("network_ok"):  # لو فيه شبكة متاحة
            logger.info("Network detected → Switching to ONLINE mode")
            mode_manager.set_mode(True)
        else:
            logger.info("No network detected → Switching to OFFLINE mode")
            mode_manager.set_mode(False)
    else:
        logger.warning("No frame captured, defaulting to OFFLINE mode")
        mode_manager.set_mode(False)

    # ----------- اختيار الـ orchestrator ----------
    if mode_manager.get_mode():
        orchestrator = OnlineOrchestrator(bus, session_store)
    else:
        orchestrator = OfflineOrchestrator(bus, session_store)

    # ----------- ربط حدث الكابتشر ----------
    def on_capture(_):
        logger.info("Capture button pressed - taking image")
        frame = camera.capture_frame()
        if frame is not None:
            result = handle_frame(frame)
            logger.info(f"Frame processed, result: {result}")
            orchestrator.on_frame_result(result)

    bus.subscribe(BTN_CAPTURE_SHORT, on_capture)

    logger.info("System ready - waiting for events")

    # ----------- loop أساسي ----------
    try:
        while True:
            pass  # لاحقاً يمكن إضافة معالجة أحداث أو وظائف أخرى
    except KeyboardInterrupt:
        logger.info("Shutting down system...")

if __name__ == "__main__":
    main()
