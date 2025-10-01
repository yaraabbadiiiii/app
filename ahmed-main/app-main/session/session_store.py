# session/session_store.py
import json, time
from pathlib import Path
from typing import Dict, Any

class SessionStore:
    """
    تخزين الحالة الحالية (mode, lineIndex, language...).
    """
    FILE = Path("session.json")

    def save_state(self, state: dict):
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"[Session] State saved: {state}")

    def load_state(self, default=None):
        if self.FILE.exists():
            with open(self.FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {} if default is None else default

    # ---- Known networks + backoff bookkeeping (kept in a sidecar file) ----
    _NET_FILE = Path("session_networks.json")

    def _load_net(self) -> Dict[str, Any]:
        if self._NET_FILE.exists():
            try:
                return json.loads(self._NET_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"known": {}, "last_attempt": {}}

    def _save_net(self, data: Dict[str, Any]) -> None:
        try:
            self._NET_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_known_networks(self) -> Dict[str, Dict[str, str]]:
        data = self._load_net()
        return dict(data.get("known", {}))

    def set_known_networks(self, known: Dict[str, Dict[str, str]]) -> None:
        data = self._load_net()
        data["known"] = dict(known)
        self._save_net(data)

    def mark_connect_attempt(self, ssid: str, ts: float | None = None) -> None:
        data = self._load_net()
        la = data.setdefault("last_attempt", {})
        la[ssid] = float(ts if ts is not None else time.time())
        self._save_net(data)

    def last_attempt_age(self, ssid: str) -> float:
        data = self._load_net()
        ts = float(data.get("last_attempt", {}).get(ssid, 0.0) or 0.0)
        if ts <= 0:
            return 1e9
        return max(0.0, time.time() - ts)
