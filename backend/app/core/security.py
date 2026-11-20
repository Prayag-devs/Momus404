"""
momus404 — app.core.security
Encryption, masking, and credential redaction engine.
Plaintext secrets are never exposed to LLM prompts, WebSocket events, or reports.
"""

from __future__ import annotations

import re
from typing import Pattern
from cryptography.fernet import Fernet
from app.core.config import get_settings

# Credential regex patterns
_REDACT_PATTERNS: list[Pattern[str]] = [
    re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.=]+"),
    re.compile(r'(?i)(api[_-]?key\s*[=:]\s*["\']?)([^"\'\s,&]+)(["\']?)'),
    re.compile(r'(?i)(password\s*[=:]\s*["\']?)([^"\'\s,&]+)(["\']?)'),
    re.compile(r"[A-Za-z0-9+/]{32,}={0,2}"),
]


def _get_fernet_instance() -> Fernet:
    settings = get_settings()
    key_str = settings.VAULT_FERNET_KEY
    if key_str:
        key_bytes = key_str.encode()
    else:
        key_bytes = Fernet.generate_key()
    return Fernet(key_bytes)


_cipher = _get_fernet_instance()


def encrypt_payload(data: str) -> bytes:
    return _cipher.encrypt(data.encode("utf-8"))


def decrypt_payload(token: bytes) -> str:
    return _cipher.decrypt(token).decode("utf-8")


def _star(s: str) -> str:
    if len(s) <= 4:
        return "***"
    return s[:2] + "***" + s[-1]


def _mask_match(match: re.Match) -> str:
    full = match.group(0)
    if match.lastindex and match.lastindex >= 2:
        prefix = match.group(1)
        secret = match.group(2)
        closing = match.group(3) if match.lastindex >= 3 and match.group(3) else ""
        return prefix + _star(secret) + closing
    if match.lastindex and match.lastindex >= 1:
        try:
            prefix = match.group(1)
            suffix = full[len(prefix):]
            return prefix + _star(suffix)
        except IndexError:
            pass
    return _star(full)


def redact(text: str) -> str:
    """Mask any credential-looking substrings in text before sending to LLM/logs."""
    if not text:
        return ""
    for pat in _REDACT_PATTERNS:
        text = pat.sub(_mask_match, text)
    return text


def mask_email(email: str) -> str:
    """Safely mask email address (e.g. u***@example.com)."""
    if not email:
        return "***"
    at = email.find("@")
    if at <= 0:
        return "***"
    return email[0] + "***" + email[at:]
