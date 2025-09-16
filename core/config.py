
import os
from pathlib import Path

# -- helpers صغيرة
_env = lambda k, d="": (v := os.getenv(k)) if (v := os.getenv(k)) not in (None, "") else d
def _env_bool(k, d=False):
    v = os.getenv(k);
    return d if v in (None, "") else v.lower() in ("1","true","yes","on")
def _env_int(k, d):
    try: return int(_env(k, str(d)))
    except: return d

# ---------- مجلدات أساسية
APP_NAME = "nabd"
HOME = Path(_env("NABD_HOME", str(Path.home() / f".{APP_NAME}"))).resolve()
DATA_DIR = HOME / "data"
LOG_DIR  = HOME / "logs"
for d in (DATA_DIR, LOG_DIR): d.mkdir(parents=True, exist_ok=True)

# ---------- لوجينغ بسيط
LOG_LEVEL = _env("NABD_LOG", "INFO")                  # DEBUG/INFO/...
LOG_FILE  = _env("NABD_LOG_FILE", str(LOG_DIR / "nabd.log"))

# ---------- جلسة
SESSION_FILE = Path(_env("NABD_SESSION_FILE", str(DATA_DIR / "session.json")))
SESSION_AUTO_SAVE_SEC = _env_int("NABD_SESSION_AUTO_SAVE_SEC", 0)  # 0 = معطّل

# ---------- لغة الفيدباك الافتراضية
DEFAULT_LANG = _env("NABD_LANG", "ar")               # "ar" أو "en"

# ---------- TTS: Piper فقط
PIPER_ENABLED   = _env_bool("NABD_PIPER_ENABLED", True)
PIPER_MODEL     = _env("NABD_PIPER_MODEL", str(DATA_DIR / "tts" / "piper" / "ar.onnx"))
PIPER_SPEAKER   = _env("NABD_PIPER_SPEAKER", "")     # إن كان الموديل multi-speaker (اختياري)
PIPER_RATE      = float(_env("NABD_PIPER_RATE", "1.0"))
PIPER_VOL       = float(_env("NABD_PIPER_VOL",  "1.0"))

# ---------- OCR/Backend (WS أو HTTP حسب ما عندك)
OCR_WS_URL      = _env("NABD_OCR_WS_URL",   "ws://127.0.0.1:8000/ws/guidance")
OCR_HTTP_URL    = _env("NABD_OCR_HTTP_URL", "http://127.0.0.1:8000/ocr")
WS_HEARTBEAT_S  = _env_int("NABD_WS_HEARTBEAT_SEC", 3)
WS_TIMEOUT_S    = _env_int("NABD_WS_TIMEOUT_SEC", 10)
CAPTURE_OCR_TIMEOUT_S = _env_int("NABD_CAPTURE_OCR_TIMEOUT_SEC", 6)

# ---------- QR (نجرّبه أولًا؛ إن فشل نكمل OCR)
QR_WIFI_PREFIXES = tuple(_env("NABD_QR_WIFI_PREFIXES", "WIFI:").split(","))
QR_IGNORE_NO_KEY = _env_bool("NABD_QR_IGNORE_NO_KEY", True)

# ---------- Offline سلوك بسيط
OFFLINE_AUTOREAD          = _env_bool("NABD_OFFLINE_AUTOREAD", True)
OFFLINE_INTERLINE_DELAY_MS= _env_int("NABD_OFFLINE_INTERLINE_MS", 0)

# ---------- Feature flags خفيفة
FEATURE_QR_FIRST         = _env_bool("NABD_FEATURE_QR_FIRST", True)
FEATURE_AUTO_SWITCH_ONLINE = _env_bool("NABD_FEATURE_AUTO_ONLINE", True)
