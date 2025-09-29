from __future__ import annotations
"""
Single-frame QR checker (no capture, no streaming).

- Presence check: OpenCV QRCodeDetector.detect (no QUIRC decode).
- Decode: pyzbar (ZBar) with multi-try fallback (resizes + adaptive threshold).
- If payload starts with WIFI:, parse via connectivity/qr_provisioning.
- If no QR: return kind="ocr" (placeholder).
"""

from dataclasses import dataclass
from typing import Any, Literal, Optional

import cv2
import numpy as np
from pyzbar.pyzbar import decode as zbar_decode

try:
    cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
except Exception:
    pass

RouteKind = Literal["wifi_qr", "other_qr", "ocr"]

@dataclass(frozen=True)
class QRDecision:
    kind: RouteKind
    payload: Optional[str] = None   # Masked for WIFI: payloads
    creds: Optional[Any] = None     # WiFiCredentials object (may contain password; do not log)
    error: Optional[str] = None     # Non-fatal notes

def _to_gray(img_rgb: np.ndarray) -> np.ndarray:
    if img_rgb.ndim == 2:
        return img_rgb
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

def _mask_wifi(payload: str) -> str:
    up = payload.upper()
    if "P:" in up:
        try:
            pref, rest = payload.split("P:", 1)
            pval, *tail = rest.split(";", 1)
            masked = "*" * min(len(pval), 8)
            return pref + "P:" + masked + (";" + tail[0] if tail else "")
        except Exception:
            pass
    return payload[:200]

def _resolve_wifi_parser():
    # Prefer class method if present
    try:
        from connectivity.qr_provisioning import QRProvisioning  # type: ignore
        if hasattr(QRProvisioning, "parse_wifi_qr"):
            return QRProvisioning.parse_wifi_qr  # type: ignore[attr-defined]
    except Exception:
        pass
    # Fall back to module-level functions
    try:
        from connectivity import qr_provisioning as qp  # type: ignore
        for name in ("parse_wifi_qr", "parse_wifi_payload", "parse"):
            fn = getattr(qp, name, None)
            if callable(fn):
                return fn
    except Exception:
        pass
    raise ImportError("No WIFI: QR parser found in connectivity/qr_provisioning.py")

def contains_qr(image_rgb: np.ndarray) -> bool:
    gray = _to_gray(image_rgb)
    det = cv2.QRCodeDetector()
    try:
        found, _pts = det.detect(gray)
    except Exception:
        try:
            _pts = det.detect(gray)
            found = _pts is not None and len(np.atleast_1d(_pts)) > 0
        except Exception:
            found = False
    return bool(found)

def _try_zbar(image_gray: np.ndarray) -> Optional[str]:
    for obj in zbar_decode(image_gray):
        try:
            data = (obj.data.decode("utf-8", "ignore") or "").strip()
        except Exception:
            data = ""
        if data:
            return data
    return None

def decode(image_rgb: np.ndarray) -> Optional[str]:
    """
    Decode first QR payload via pyzbar (ZBar).
    Fallbacks: multi-scale and adaptive threshold if the first pass fails.
    """
    gray = _to_gray(image_rgb)

    # 1) Raw
    data = _try_zbar(gray)
    if data:
        return data

    # 2) Multi-scale (down/up) – ZBar tends to like certain sizes
    for scale in (0.75, 0.5, 1.25, 1.5):
        h, w = gray.shape[:2]
        resized = cv2.resize(
            gray,
            (max(1, int(w * scale)), max(1, int(h * scale))),
            interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR,
        )
        data = _try_zbar(resized)
        if data:
            return data

    # 3) Adaptive threshold (and inverted)
    thr = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 5
    )
    data = _try_zbar(thr) or _try_zbar(255 - thr)
    return data

def classify_frame(image_rgb: np.ndarray) -> QRDecision:
    if not contains_qr(image_rgb):
        return QRDecision(kind="ocr")  # No QR → OCR later
    payload = decode(image_rgb)
    if not payload:
        return QRDecision(kind="other_qr", error="qr_detected_but_decode_failed")
    if payload.upper().startswith("WIFI:"):
        try:
            parse_wifi = _resolve_wifi_parser()
            creds = parse_wifi(payload)
            if creds:
                return QRDecision(kind="wifi_qr", payload=_mask_wifi(payload), creds=creds)
            return QRDecision(kind="other_qr", payload=_mask_wifi(payload), error="wifi_parse_returned_none")
        except Exception as e:
            return QRDecision(kind="other_qr", payload=_mask_wifi(payload), error=f"wifi_parse_error:{e}")
    return QRDecision(kind="other_qr", payload=payload[:200])
