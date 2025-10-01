import sys
import time
from typing import Optional


def beep(kind: str = "info", *, duration_ms: int = 80) -> None:
    try:
        sys.stdout.write(f"[beep] {kind}\n")
        sys.stdout.flush()
        time.sleep(max(0.0, duration_ms / 1000.0))
    except Exception:
        pass


class BeepService:
    def __init__(self):
        self._stopped = False

    def speak(self, text: str) -> None:
        if self._stopped:
            return
        sys.stdout.write(f"[tts] {text}\n")
        sys.stdout.flush()
        beep("tts")

    def stop(self) -> None:
        self._stopped = True


