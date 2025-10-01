import logging, threading, time
from core.bus import EventBus
from core.config import APP_NAME
from core.events import (
    BTN_CAPTURE_SHORT, BTN_CAPTURE_LONG, BTN_CAPTURE_DOUBLE,
    BTN_NEXT_SHORT, BTN_PREV_SHORT, BTN_NEXT_LONG, BTN_PREV_LONG,
    NET_ONLINE, NET_OFFLINE, NET_SCAN_TICK,
)
from session.session_store import SessionStore
from mode.mode_manger import ModeManager
from services.audio.beep_service import BeepService
from services.camera.camera import Camera
from connectivity.network import handle_frame, is_online, scan
from services.vision.qr_detector import classify_frame
from services.vision.ocr import run_ocr_placeholder
from mode.online import OnlineOrchestrator
from mode.offline import OfflineOrchestrator



def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(APP_NAME)
    logger.info("Starting AI Reader System")

    bus = EventBus()
    session_store = SessionStore()

    # Minimal TTS via BeepService (provides speak/stop for offline)
    tts = BeepService()

    # Orchestrators
    offline_mode = OfflineOrchestrator(bus, tts, session_store)
    online_mode = OnlineOrchestrator(bus)

    # Mode manager controls active mode
    mode_manager = ModeManager(bus, offline_mode, online_mode, is_online_provider=is_online)

    camera = Camera(bus)

    # 1) System check/logging already initialized above

    # 2) Internet Connectivity Check
    online_now = is_online()
    bus.emit(NET_ONLINE if online_now else NET_OFFLINE, {"online": online_now})

    # 3) WiFi Network Scan (initial)
    try:
        ssids = scan()
    except Exception:
        ssids = []
    bus.emit(NET_SCAN_TICK, {"ssids": ssids})

    # 4) Connection Status already determined via online_now

    # 5) Mode Selection
    if online_now:
        logger.info("Preparing ONLINE mode")
        mode_manager.switch_to_online()
    else:
        logger.info("Entering OFFLINE mode")
        mode_manager.switch_to_offline()

    # Background watcher for offline monitoring (ping + scan)
    stop_event = threading.Event()

    def net_watcher():
        last_online = online_now
        while not stop_event.is_set():
            now_online = is_online()
            if now_online != last_online:
                bus.emit(NET_ONLINE if now_online else NET_OFFLINE, {"online": now_online})
                last_online = now_online
            try:
                ss = scan()
            except Exception:
                ss = []
            bus.emit(NET_SCAN_TICK, {"ssids": ss})
            time.sleep(3.0)

    threading.Thread(target=net_watcher, name="net-watcher", daemon=True).start()

    def on_capture(_):
        logger.info("Capture button pressed - taking image")
        frame = camera.capture()
        if frame is not None:
            # First classify for QR; if not WIFI QR, fallback to OCR placeholder
            try:
                decision = classify_frame(frame)
            except Exception as e:
                logger.warning(f"QR classify failed: {e}")
                decision = None
            if decision and getattr(decision, "kind", "") == "wifi_qr":
                result = handle_frame(frame)
                logger.info(f"QR handled via network; result: {result}")
            else:
                lines = run_ocr_placeholder(frame)
                logger.info(f"OCR produced {len(lines)} lines")
                bus.emit("OCR_DONE", {"lines": lines})

    def on_capture_long(_):
        logger.info("Capture long - switch feedback language (placeholder)")

    def on_capture_double(_):
        logger.info("Capture double - request online mode if internet available")
        if is_online():
            mode_manager.switch_to_online()
        else:
            logger.info("Still offline")

    bus.subscribe(BTN_CAPTURE_SHORT, on_capture)
    bus.subscribe(BTN_CAPTURE_LONG, on_capture_long)
    bus.subscribe(BTN_CAPTURE_DOUBLE, on_capture_double)
    # Other buttons are handled inside OfflineOrchestrator already

    logger.info("System ready - waiting for events")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("Shutting down system...")
        stop_event.set()

if __name__ == "__main__":
    main()



