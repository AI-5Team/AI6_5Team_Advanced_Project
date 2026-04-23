from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.database import get_connection, utc_now
from app.core.security import generate_session_token, hash_token

_TOKEN_TTL_SEC = 3600  # 1시간


def issue_token(user_id: str, purpose: str) -> str:
    token = generate_session_token()
    token_hash = hash_token(token)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=_TOKEN_TTL_SEC)).isoformat()
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO verification_tokens (id, user_id, token_hash, purpose, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid4()), user_id, token_hash, purpose, expires_at, now),
        )
    return token


def issue_email_verify(user_id: str) -> str:
    return issue_token(user_id, "verify_email")


def issue_password_reset(user_id: str) -> str:
    return issue_token(user_id, "reset_password")


def consume_token(token: str, purpose: str) -> str:
    """토큰을 소비하고 user_id를 반환합니다. 실패 시 ValueError."""
    token_hash = hash_token(token)
    now = utc_now()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, expires_at, used_at
            FROM verification_tokens
            WHERE token_hash = ? AND purpose = ?
            """,
            (token_hash, purpose),
        ).fetchone()
        if row is None:
            raise ValueError("invalid token")
        if row["used_at"] is not None:
            raise ValueError("token already used")
        if row["expires_at"] < now:
            raise ValueError("token expired")
        conn.execute(
            "UPDATE verification_tokens SET used_at = ? WHERE id = ?",
            (now, row["id"]),
        )
        return row["user_id"]
