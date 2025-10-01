import logging
from core.bus import EventBus
from core.config import APP_NAME
from core.events import BTN_CAPTURE_SHORT
from core.storge import SessionStore
from mode.mode_manger import ModeManager
from services.beep_service import BeepService
from services.camera import Camera
from services.vision.qr_detector import classify_frame
from connectivity.network import handle_frame
from mode.online import Online
from mode.offline import Offline
  


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(APP_NAME)
    logger.info("Starting AI Reader System")

    bus = EventBus()
    session_store = SessionStore()
    mode_manager = ModeManager()

    camera = Camera(bus)
    vision = VisionService(bus)
    audio = BeepService(bus)

    logger.info("Checking network mode via QR...")
    first_frame = camera.capture()

    if first_frame is not None:
        qr_result = handle_frame(first_frame)
        if qr_result and qr_result.get("network_ok"):
            logger.info("Network detected → Switching to ONLINE mode")
            mode_manager.set_mode(True)
        else:
            logger.info("No network detected → Switching to OFFLINE mode")
            mode_manager.set_mode(False)
    else:
        logger.warning("No frame captured, defaulting to OFFLINE mode")
        mode_manager.set_mode(False)

    if mode_manager.get_mode():
        orchestrator = OnlineOrchestrator(bus, session_store)
    else:
        orchestrator = OfflineOrchestrator(bus, session_store)

    def on_capture(_):
        logger.info("Capture button pressed - taking image")
        frame = camera.capture()
        if frame is not None:
            result = handle_frame(frame)
            logger.info(f"Frame processed, result: {result}")
            orchestrator.on_frame_result(result)

    bus.subscribe(BTN_CAPTURE_SHORT, on_capture)

    logger.info("System ready - waiting for events")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Shutting down system...")

if __name__ == "__main__":
    main()




