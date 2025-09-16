# main.py
from core.bus import EventBus
from core import events as E
from services.tts import TTS
from core.storage import SessionStore
from mode.offline import OfflineOrchestrator
from mode.mode_manager import ModeManager
from services.io.buttons import Buttons
from services.camera.camera import Camera
from services.io.volume import Volume

def main():
    bus = EventBus()
    tts = TTS()
    session_store = SessionStore()

    # Orchestrator + ModeManager
    orchestrator = OfflineOrchestrator(bus, tts, session_store)
    mode_manager = ModeManager(bus, orchestrator)  # online ممكن تضيفه لاحقًا

    buttons = Buttons(bus)
    camera = Camera(bus)
    volume = Volume(bus)

    print("\n--- Boot Sequence ---")
    tts.speak("System check in progress...")

    print("\n--- Network OFFLINE ---")
    bus.emit(E.NET_STATUS, {"online": False})

    print("\n--- Capture Image ---")
    buttons.press_capture("short")
    camera.capture(has_text=True)

    print("\n--- Network ONLINE ---")
    bus.emit(E.NET_STATUS, {"online": True})

    print("\n--- Network OFFLINE Again ---")
    bus.emit(E.NET_STATUS, {"online": False})

if __name__ == "__main__":
    main()
