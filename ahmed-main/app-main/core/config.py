import os
from pathlib import Path

_env = lambda k, d="": (v := os.getenv(k)) if (v := os.getenv(k)) not in (None, "") else d
def _env_bool(k, d=False):
    v = os.getenv(k)
    return d if v in (None, "") else v.lower() in ("1", "true", "yes", "on")
def _env_int(k, d):
    try: 
        return int(_env(k, str(d)))
    except: 
        return d

APP_NAME = "nabd"
HOME = Path(_env("NABD_HOME", str(Path.home() / f".{APP_NAME}"))).resolve()
DATA_DIR = HOME / "data"
LOG_DIR  = HOME / "logs"
for d in (DATA_DIR, LOG_DIR): 
    d.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = _env("NABD_LOG", "INFO")
LOG_FILE  = _env("NABD_LOG_FILE", str(LOG_DIR / "nabd.log"))

SESSION_FILE = Path(_env("NABD_SESSION_FILE", str(DATA_DIR / "session.json")))
SESSION_AUTO_SAVE_SEC = _env_int("NABD_SESSION_AUTO_SAVE_SEC", 0)

DEFAULT_LANG = _env("NABD_LANG", "ar")

PIPER_ENABLED   = _env_bool("NABD_PIPER_ENABLED", True)
PIPER_MODEL     = _env("NABD_PIPER_MODEL", str(DATA_DIR / "tts" / "piper" / "ar.onnx"))
PIPER_SPEAKER   = _env("NABD_PIPER_SPEAKER", "")
PIPER_RATE      = float(_env("NABD_PIPER_RATE", "1.0"))
PIPER_VOL       = float(_env("NABD_PIPER_VOL",  "1.0"))

QR_WIFI_PREFIXES = tuple(_env("NABD_QR_WIFI_PREFIXES", "WIFI:").split(","))
QR_IGNORE_NO_KEY = _env_bool("NABD_QR_IGNORE_NO_KEY", True)

OFFLINE_AUTOREAD           = _env_bool("NABD_OFFLINE_AUTOREAD", True)
OFFLINE_INTERLINE_DELAY_MS = _env_int("NABD_OFFLINE_INTERLINE_MS", 0)

FEATURE_QR_FIRST           = _env_bool("NABD_FEATURE_QR_FIRST", True)
FEATURE_AUTO_SWITCH_ONLINE = _env_bool("NABD_FEATURE_AUTO_ONLINE", True)

# -------- Auto-connect (offline) --------
# Static known networks can be provided via ENV as JSON if desired; fallback to empty dict
import json as _json
try:
    KNOWN_NETWORKS = _json.loads(_env("NABD_KNOWN_NETWORKS", "{}"))
except Exception:
    KNOWN_NETWORKS = {}

AUTOCONNECT_SCAN_INTERVAL_S = _env_int("NABD_AUTOCONNECT_SCAN_INTERVAL_S", 7)
AUTOCONNECT_BACKOFF_S       = _env_int("NABD_AUTOCONNECT_BACKOFF_S", 30)

