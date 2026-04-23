from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque


@dataclass
class _Window:
    timestamps: Deque[float] = field(default_factory=deque)


_lock = Lock()
_store: dict[str, _Window] = defaultdict(_Window)


def _clean_and_count(key: str, window_sec: float, now: float) -> int:
    w = _store[key]
    cutoff = now - window_sec
    while w.timestamps and w.timestamps[0] < cutoff:
        w.timestamps.popleft()
    return len(w.timestamps)


def check_rate_limit(key: str, limit: int, window_sec: float) -> bool:
    """Return True if the request is allowed, False if rate-limited."""
    now = time.monotonic()
    with _lock:
        count = _clean_and_count(key, window_sec, now)
        if count >= limit:
            return False
        _store[key].timestamps.append(now)
        return True


# Spec-defined limits
#   /api/auth/login          — IP:  10/min,  email: 5/min
#   /api/auth/register       — IP:  5/min
#   /api/auth/password/...   — IP:  3/min,  email: 3/hr

def allow_login(ip: str, email: str) -> bool:
    return (
        check_rate_limit(f"login_ip:{ip}", 10, 60)
        and check_rate_limit(f"login_email:{email}", 5, 60)
    )


def allow_register(ip: str) -> bool:
    return check_rate_limit(f"register_ip:{ip}", 5, 60)


def allow_password_reset(ip: str, email: str) -> bool:
    return (
        check_rate_limit(f"pwreset_ip:{ip}", 3, 60)
        and check_rate_limit(f"pwreset_email:{email}", 3, 3600)
    )
