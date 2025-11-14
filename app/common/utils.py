"""Helper signatures: now_ms, b64e, b64d, sha256_hex."""

import time
import base64
import hashlib


def now_ms() -> int:
    """Get current time in milliseconds since Unix epoch."""
    return int(time.time() * 1000)


def b64e(b: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(b).decode('utf-8')


def b64d(s: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(s)


def sha256_hex(data: bytes) -> str:
    """Compute SHA-256 hash and return as hexadecimal string."""
    return hashlib.sha256(data).hexdigest()
