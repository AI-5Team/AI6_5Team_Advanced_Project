from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from app.core.config import get_settings
from app.core.database import get_connection, utc_now
from app.core.security import generate_session_token, hash_token


def issue_session(
    *,
    user_id: str,
    ip: str | None = None,
    user_agent: str | None = None,
) -> str:
    token = generate_session_token()
    token_hash = hash_token(token)
    settings = get_settings()
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=settings.session_ttl_sec)).isoformat()
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (id, user_id, session_token_hash, ip_address, user_agent, expires_at, last_used_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid4()), user_id, token_hash, ip, user_agent, expires_at, now, now),
        )
    return token


def verify_session(token: str) -> dict[str, Any] | None:
    token_hash = hash_token(token)
    now = utc_now()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT s.id, s.user_id, s.expires_at, s.revoked_at,
                   u.email, u.name, u.status, u.deleted_at
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.session_token_hash = ?
            """,
            (token_hash,),
        ).fetchone()
        if row is None:
            return None
        if row["revoked_at"] is not None:
            return None
        if row["expires_at"] < now:
            return None
        if row["deleted_at"] is not None:
            return None
        if row["status"] != "active":
            return None
        conn.execute(
            "UPDATE sessions SET last_used_at = ? WHERE id = ?",
            (now, row["id"]),
        )
        return {
            "sessionId": row["id"],
            "userId": row["user_id"],
            "email": row["email"],
            "name": row["name"],
        }


def revoke_session(session_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET revoked_at = ? WHERE id = ?",
            (utc_now(), session_id),
        )


def revoke_session_by_token(token: str) -> None:
    token_hash = hash_token(token)
    with get_connection() as conn:
        conn.execute(
            "UPDATE sessions SET revoked_at = ? WHERE session_token_hash = ?",
            (utc_now(), token_hash),
        )


def revoke_all_sessions(user_id: str, except_session_id: str | None = None) -> None:
    now = utc_now()
    with get_connection() as conn:
        if except_session_id:
            conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND id != ? AND revoked_at IS NULL",
                (now, user_id, except_session_id),
            )
        else:
            conn.execute(
                "UPDATE sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL",
                (now, user_id),
            )
