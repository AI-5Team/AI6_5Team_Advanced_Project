from __future__ import annotations

import json
from typing import Any

from app.core.database import get_connection, utc_now

_SENSITIVE_KEYS = frozenset({
    "password", "password_hash", "token", "access_token", "refresh_token",
    "session_token", "card_number", "cvc", "cvv", "secret",
})


def sanitize_metadata(data: dict[str, Any]) -> dict[str, Any]:
    return {
        k: "[REDACTED]" if k.lower() in _SENSITIVE_KEYS else v
        for k, v in data.items()
    }


def log_event(
    *,
    event_type: str,
    user_id: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    sanitized = sanitize_metadata(metadata) if metadata else None
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO audit_logs (user_id, event_type, ip_address, user_agent, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, event_type, ip, user_agent, json.dumps(sanitized) if sanitized else None, now),
        )
