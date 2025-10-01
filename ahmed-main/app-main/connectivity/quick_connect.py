from __future__ import annotations

import subprocess
import time
from typing import Optional

from service import qr_checker


def _run(cmd: list[str], *, timeout: Optional[float] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout
    )


def _nmcli_connect(ssid: str | None, password: Optional[str], *, hidden: bool = False) -> bool:
    if not ssid:
        return False
    args = ["nmcli", "dev", "wifi", "connect", ssid]
    if password:
        args += ["password", password]
    if hidden:
        args += ["hidden", "yes"]
    proc = _run(args, timeout=20)
    if proc.returncode != 0:
        # show a short diagnostic from nmcli (no secrets)
        last = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:] or ["nmcli failed"]
        print(f"[nmcli] rc={proc.returncode} err={' | '.join(last)}")
    return proc.returncode == 0


def _is_online(host: str = "8.8.8.8", count: int = 1, timeout_s: float = 1.0) -> bool:
    """Simple ICMP reachability check."""
    try:
        proc = _run(["ping", "-c", str(count), "-W", str(int(timeout_s)), host], timeout=timeout_s + 0.5)
        return proc.returncode == 0
    except Exception:
        return False


def connect_via_qr_frame(image_rgb, *, wait_s: float = 8.0) -> bool:
    """
    Decode a single RGB frame (np.ndarray). If it's a WIFI: QR,
    run nmcli connect and wait briefly for internet.
    """
    d = qr_checker.classify_frame(image_rgb)
    if d.kind != "wifi_qr" or d.creds is None:
        return False

    ssid = getattr(d.creds, "ssid", None)
    password = getattr(d.creds, "password", None)
    hidden = bool(getattr(d.creds, "hidden", False))

    if not _nmcli_connect(ssid, password, hidden=hidden):
        return False

    deadline = time.time() + max(1.0, wait_s)
    while time.time() < deadline:
        if _is_online():
            return True
        time.sleep(0.6)
    return False


