from __future__ import annotations
"""
Network orchestrator (camera-agnostic for button frames; optional camera watcher).

- Online check via ping.
- Accepts single captured frames (RGB np.ndarray) and routes them through qr_checker.
- For WIFI: QR -> nmcli connect -> verify internet.
- Optional: ensure_online() (blocking) and start_qr_online_task() (background watcher) for hands-free QR provisioning.

Passwords are never logged.
"""

import logging, subprocess, threading, time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from service import qr_checker
from service.logging_setup import setup_logging

try:
    from service.audio import beep as _beep
except Exception:
    def _beep(_: str, **__: Any) -> None: pass

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class NmcliResult:
    ok: bool; rc: int; out: str; err: str

def _run(cmd: list[str], *, timeout: Optional[float] = None) -> NmcliResult:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
    return NmcliResult(ok=(p.returncode == 0), rc=p.returncode, out=p.stdout.strip(), err=p.stderr.strip())

def is_online(host: str = "8.8.8.8", count: int = 1, timeout_s: float = 1.0) -> bool:
    try:
        r = _run(["ping","-c",str(count),"-W",str(int(timeout_s)),host], timeout=timeout_s+0.5)
        logger.debug("ping rc=%s out='%s' err='%s'", r.rc, r.out, r.err)
        return r.ok
    except Exception as e:
        logger.warning("ping failed: %s", repr(e)); return False

def get_active_ssid() -> Optional[str]:
    r = _run(["nmcli","-t","-f","ACTIVE,SSID","dev","wifi"])
    if not r.ok: return None
    for line in r.out.splitlines():
        parts = line.split(":")
        if len(parts) >= 2 and parts[0] == "yes":
            return parts[1] or None
    return None

def scan() -> list[str]:
    r = _run(["nmcli","-t","-f","SSID","dev","wifi","list"])
    if not r.ok: return []
    out: list[str] = []
    for line in r.out.splitlines():
        s = (line or "").strip()
        if s and s not in out: out.append(s)
    return out

def _nmcli_connect(ssid: str | None, password: Optional[str], *, hidden: bool = False) -> NmcliResult:
    args = ["nmcli","dev","wifi","connect", ssid or ""]
    if password: args += ["password", password]
    if hidden: args += ["hidden","yes"]
    return _run(args, timeout=20)

# ------- Camera-agnostic, single-frame entrypoint (use this from your button) --------

def handle_frame(image_rgb: "Any", *, connect_wait_s: float = 8.0, ping_timeout_s: float = 1.0) -> qr_checker.QRDecision:
    """
    Route a captured RGB frame:
      - No QR -> emits 'ocr_route' and returns decision (placeholder for OCR).
      - Other QR -> emits 'other_qr'.
      - WIFI QR -> nmcli connect and confirm internet, emits 'nmcli_connect_ok' and 'online_after_qr'.
    """
    setup_logging()
    d = qr_checker.classify_frame(image_rgb)

    if d.kind == "ocr":
        logger.info("ocr_route")
        _beep("qr_invalid_payload")
        return d

    if d.kind == "other_qr":
        note = d.error or (d.payload or "<unknown_qr>")
        logger.info("other_qr %s", note)
        _beep("qr_invalid_payload")
        return d

    # WIFI QR path
    creds = d.creds
    ssid = getattr(creds, "ssid", None)
    hidden = bool(getattr(creds, "hidden", False))
    password = getattr(creds, "password", None)

    logger.info("qr_valid_payload ssid=%s hidden=%s", ssid, hidden)
    _beep("qr_valid_payload")

    active = get_active_ssid()
    if ssid and active and ssid != active:
        logger.info("switching_ssid frm=%s to=%s", active, ssid)
        _beep("switching_ssid")

    r = _nmcli_connect(ssid, password, hidden=hidden)
    if not r.ok:
        logger.info("nmcli_connect_failed ssid=%s rc=%d", ssid, r.rc)
        _beep("nmcli_connect_failed")
        return d

    logger.info("nmcli_connect_ok ssid=%s", ssid)
    _beep("nmcli_connect_ok")

    deadline = time.time() + max(1.0, connect_wait_s)
    while time.time() < deadline:
        if is_online(timeout_s=ping_timeout_s):
            logger.info("online_after_qr ssid=%s", ssid)
            _beep("online_after_qr")
            return d
        time.sleep(0.6)

    logger.info("still_offline_after_connect ssid=%s", ssid)
    return d

# ------- OPTIONAL: camera-backed helpers if you also want hands-free provisioning ----
# These keep qr_checker image-only; they capture frames here and pass them in.

def ensure_online(*, autoconnect_window_s: float = 6.0, camera_warmup_s: float = 1.2) -> bool:
    """Blocking: allow autoconnect window; if offline, wait for a WIFI: QR via camera and connect."""
    setup_logging()
    end = time.time() + autoconnect_window_s
    while time.time() < end:
        if is_online():
            logger.info("already_online"); _beep("online_after_qr"); return True
        time.sleep(0.5)

    try:
        from picamera2 import Picamera2
    except Exception:
        logger.error("picamera2 not available"); return False

    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"format":"RGB888"}))
    cam.start(); time.sleep(camera_warmup_s)
    try:
        while True:
            frame = cam.capture_array()
            d = handle_frame(frame)
            if d.kind == "wifi_qr" and is_online(): return True
            time.sleep(0.3)
    finally:
        try: cam.close()
        except Exception: pass

def start_qr_online_task(*, debounce_s: float = 6.0, camera_warmup_s: float = 1.2) -> threading.Thread:
    """Background watcher: scans via camera; connects/switches when a WIFI: QR appears."""
    setup_logging()
    try:
        from picamera2 import Picamera2
    except Exception:
        raise RuntimeError("picamera2 not available")

    stop = threading.Event()

    def loop() -> None:
        cam = Picamera2()
        cam.configure(cam.create_preview_configuration(main={"format":"RGB888"}))
        cam.start(); time.sleep(camera_warmup_s)
        last_ssid: Optional[str] = None
        last_ts = 0.0
        try:
            while not stop.is_set():
                frame = cam.capture_array()
                d = qr_checker.classify_frame(frame)
                if d.kind != "wifi_qr":
                    time.sleep(0.4); continue
                ssid = getattr(d.creds, "ssid", None)
                now = time.time()
                if ssid and ssid == last_ssid and (now - last_ts) < debounce_s:
                    time.sleep(0.4); continue
                last_ssid, last_ts = ssid, now
                handle_frame(frame)  # emits events + connects
                time.sleep(0.4)
        finally:
            try: cam.close()
            except Exception: pass

    th = threading.Thread(target=loop, name="qr-online-task", daemon=True)
    th.stop_event = stop  # type: ignore[attr-defined]
    th.start()
    return th

