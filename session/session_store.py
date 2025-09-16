# session/session_store.py
import json
from pathlib import Path

class SessionStore:
    """
    تخزين الحالة الحالية (mode, lineIndex, language...).
    """
    FILE = Path("session.json")

    def save_state(self, state: dict):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"[Session] State saved: {state}")

    def load_state(self):
        if self.FILE.exists():
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
