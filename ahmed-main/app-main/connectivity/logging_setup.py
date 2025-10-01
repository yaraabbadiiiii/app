from __future__ import annotations
import logging, os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

def _writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        t = path / ".write_test"
        t.write_text("ok"); t.unlink(missing_ok=True)
        return True
    except Exception:
        return False

def setup_logging(level: int = logging.INFO, *, name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name) if name else logging.getLogger()
    if logger.handlers:  # already configured
        logger.setLevel(level); return logger
    logger.setLevel(level)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    sh = logging.StreamHandler(); sh.setLevel(level); sh.setFormatter(fmt); logger.addHandler(sh)

    log_dir = Path(os.environ.get("AI_READER_LOG_DIR", "/var/log/ai-reader"))
    if not _writable_dir(log_dir):
        log_dir = Path("./logs"); _writable_dir(log_dir)
    fh = RotatingFileHandler(log_dir / "ai-reader.log", maxBytes=1_000_000, backupCount=5)
    fh.setLevel(level); fh.setFormatter(fmt); logger.addHandler(fh)

    # tame chatty libs
    logging.getLogger("cv2").setLevel(logging.ERROR)
    logging.getLogger("pyzbar").setLevel(logging.WARNING)
    return logger
