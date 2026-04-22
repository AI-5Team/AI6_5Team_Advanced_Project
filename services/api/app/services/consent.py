from __future__ import annotations

from uuid import uuid4

from app.core.database import get_connection, utc_now

CURRENT_CONSENT_VERSIONS = {
    "terms": "2026-04-22",
    "privacy": "2026-04-22",
    "age_14": "2026-04-22",
    "overseas_transfer": "2026-04-22",
}

REQUIRED_CONSENT_TYPES = ("terms", "privacy", "age_14", "overseas_transfer")


def record_signup_consents(
    *,
    user_id: str,
    ip: str,
    user_agent: str | None,
) -> None:
    now = utc_now()
    with get_connection() as conn:
        for consent_type in REQUIRED_CONSENT_TYPES:
            conn.execute(
                """
                INSERT INTO consents (id, user_id, consent_type, version, agreed, agreed_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    user_id,
                    consent_type,
                    CURRENT_CONSENT_VERSIONS[consent_type],
                    now,
                    ip,
                    user_agent,
                ),
            )


def has_agreed(user_id: str, consent_type: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT agreed FROM consents
            WHERE user_id = ? AND consent_type = ?
            ORDER BY agreed_at DESC LIMIT 1
            """,
            (user_id, consent_type),
        ).fetchone()
        return bool(row and row["agreed"])


def revoke_consent(user_id: str, consent_type: str, ip: str, user_agent: str | None) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO consents (id, user_id, consent_type, version, agreed, agreed_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, 0, ?, ?, ?)
            """,
            (
                str(uuid4()),
                user_id,
                consent_type,
                CURRENT_CONSENT_VERSIONS.get(consent_type, "unknown"),
                utc_now(),
                ip,
                user_agent,
            ),
        )
