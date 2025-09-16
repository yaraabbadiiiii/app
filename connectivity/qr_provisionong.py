from __future__ import annotations
"""
Wi-Fi QR provisioning parser.

Supports Android-style WIFI: payloads with fields in any order:
  - T: security type (WPA|WPA2|WPA3|SAE|WEP|nopass)
  - S: SSID
  - P: password (optional if T:nopass)
  - H: hidden (true/false/1/0/yes/no)

Escaping:
  - '\;' represents a literal ';'
  - '\:' represents a literal ':'
  - '\\' represents a literal '\'

Examples:
  WIFI:T:WPA;S:MyNet;P:pass123;;
  WIFI:S:Guest;T:nopass;H:true;;
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class WiFiCredentials:
    ssid: str
    security: str
    password: Optional[str]
    hidden: bool


# ---------- internal helpers --------------------------------------------------

def _unescape(s: str) -> str:
    """Unescape \;  \:  \\ sequences."""
    out: list[str] = []
    it = iter(range(len(s)))
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt in (";", ":", "\\"):
                out.append(nxt)
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _split_pairs(body: str) -> Dict[str, str]:
    """
    Split WIFI body (after 'WIFI:') into key:value pairs handling escapes.
    Pairs are separated by unescaped ';' and key/value by unescaped ':'.
    """
    pairs: Dict[str, str] = {}

    token = []
    i = 0
    n = len(body)

    def flush(tok: str) -> None:
        if not tok:
            return
        # split on first unescaped ':'
        k = []
        v = []
        j = 0
        while j < len(tok):
            ch = tok[j]
            if ch == "\\" and j + 1 < len(tok):
                # keep escape for now; _unescape() later
                if v:
                    v.append(ch)
                else:
                    k.append(ch)
                j += 1
                # append next literal
                if v:
                    v.append(tok[j])
                else:
                    k.append(tok[j])
                j += 1
                continue
            if ch == ":":
                # first unescaped ':' splits key/value
                v.extend(tok[j + 1 :])
                break
            k.append(ch)
            j += 1
        key = "".join(k).strip().upper()
        val = _unescape("".join(v)).strip()
        if key:
            pairs[key] = val

    while i < n:
        ch = body[i]
        if ch == "\\" and i + 1 < n:
            token.append(ch)
            token.append(body[i + 1])
            i += 2
            continue
        if ch == ";":
            flush("".join(token))
            token = []
            i += 1
            continue
        token.append(ch)
        i += 1

    # trailing token (before optional final ';')
    flush("".join(token))
    return pairs


def _normalize_security(t: str) -> str:
    t_up = t.strip().upper()
    if t_up in {"WPA3", "SAE"}:
        return "WPA3"
    if t_up in {"WPA2", "RSN"}:
        return "WPA2"
    if t_up in {"WPA"}:
        return "WPA"
    if t_up in {"WEP"}:
        return "WEP"
    if t_up in {"NOPASS", "OPEN"}:
        return "nopass"
    # default to WPA for unknown but present values
    return t_up or "WPA"


def _parse_hidden(h: str) -> bool:
    return h.strip().lower() in {"1", "true", "yes", "y"}


# ---------- public API --------------------------------------------------------

def parse_wifi_qr(payload: str) -> WiFiCredentials:
    """
    Parse a WIFI: payload into WiFiCredentials.
    Raises ValueError on invalid inputs. Never prints passwords.
    """
    if not isinstance(payload, str):
        raise ValueError("payload must be a string")
    p = payload.strip()
    if not p.upper().startswith("WIFI:"):
        raise ValueError("not a WIFI: payload")

    body = p[5:]  # strip 'WIFI:'
    pairs = _split_pairs(body)

    ssid = _unescape(pairs.get("S", ""))
    sec = _normalize_security(pairs.get("T", "WPA"))
    hidden = _parse_hidden(pairs.get("H", "false"))

    pwd_raw = pairs.get("P", None)
    password = _unescape(pwd_raw) if pwd_raw is not None else None

    if not ssid:
        raise ValueError("missing SSID (S)")
    if sec != "nopass" and not password:
        raise ValueError("missing password (P) for secured network")

    return WiFiCredentials(ssid=ssid, security=sec, password=password, hidden=hidden)


# Backwards-compatible aliases expected by other modules/scripts
def parse_wifi_payload(payload: str) -> WiFiCredentials:
    return parse_wifi_qr(payload)


def parse(payload: str) -> WiFiCredentials:
    return parse_wifi_qr(payload)


class QRProvisioning:
    """Optional class-based API for callers that expect QRProvisioning.parse_wifi_qr()."""

    @staticmethod
    def parse_wifi_qr(payload: str) -> WiFiCredentials:
        return parse_wifi_qr(payload)
