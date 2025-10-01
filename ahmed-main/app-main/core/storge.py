   # core/storage.py
import json
import os

class SessionStore:
    def __init__(self, file_path="data/session.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def save_state(self, state: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self, default=None) -> dict:
        if not os.path.exists(self.file_path):
            return default or {}
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
