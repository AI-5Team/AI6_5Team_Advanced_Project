from __future__ import annotations

import os
import secrets
from base64 import b64decode, b64encode
from datetime import datetime, timezone
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings
from app.core.database import get_connection, utc_now


class NotConnectedError(Exception):
    """OAuth connection is missing or expired and cannot be refreshed."""


_IV_LEN = 12
_TAG_LEN = 16


def _get_key() -> bytes:
    raw = get_settings().token_encryption_key
    key = bytes.fromhex(raw)
    if len(key) != 32:
        raise ValueError("TOKEN_ENCRYPTION_KEY must be 32 bytes (64 hex chars)")
    return key


def encrypt_token(plain: str) -> str:
    """Return base64( iv(12) | ciphertext+tag ) — safe for TEXT columns."""
    key = _get_key()
    iv = os.urandom(_IV_LEN)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(iv, plain.encode("utf-8"), None)
    blob = iv + ciphertext_with_tag
    return b64encode(blob).decode("ascii")


def decrypt_token(encoded: str) -> str:
    """Inverse of encrypt_token. Raises ValueError on tampered / wrong-key data."""
    key = _get_key()
    blob = b64decode(encoded.encode("ascii"))
    if len(blob) < _IV_LEN + _TAG_LEN:
        raise ValueError("encrypted token blob too short")
    iv = blob[:_IV_LEN]
    ciphertext_with_tag = blob[_IV_LEN:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ciphertext_with_tag, None).decode("utf-8")


def _is_expiring_soon(token_expires_at: str | None) -> bool:
    if not token_expires_at:
        return False
    try:
        expires = datetime.fromisoformat(token_expires_at)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (expires - now).total_seconds() < 300  # 5-minute buffer
    except ValueError:
        return False


def _simulate_token_refresh(channel: str, _refresh_token: str) -> dict[str, Any]:
    """
    Placeholder for real OAuth refresh flow.
    In production, call the provider's token endpoint with the refresh_token.
    Returns {"access_token": str, "refresh_token": str | None, "expires_in": int}
    """
    from datetime import timedelta
    # Demo: extend by 7 days
    return {
        "access_token": f"{channel}-refreshed-{secrets.token_hex(8)}",
        "refresh_token": None,
        "expires_in": 7 * 24 * 3600,
    }


def get_valid_access_token(user_id: str, provider: str) -> str:
    """
    Return a valid plaintext OAuth access token for the given user + provider.

    Raises NotConnectedError if the account is not connected or refresh fails.
    This is the single function the automation team calls — do not call encrypt_token
    or decrypt_token directly from other services.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM social_accounts WHERE user_id = ? AND channel = ?",
            (user_id, provider),
        ).fetchone()

    if not row or row["status"] not in ("connected", "expired"):
        raise NotConnectedError(f"{provider} 계정이 연결되지 않았습니다.")

    if not row["access_token_ref"]:
        raise NotConnectedError(f"{provider} 액세스 토큰이 없습니다.")

    access_token = decrypt_token(row["access_token_ref"])

    if _is_expiring_soon(row["token_expires_at"]):
        if not row["refresh_token_ref"]:
            raise NotConnectedError(f"{provider} 토큰이 만료되었고 갱신 토큰이 없습니다.")
        # 운영 전환 시에는 user+provider 기준 분산 락이 필요하지만, 현재 데모 범위에서는 단일 프로세스 갱신으로 유지합니다.
        try:
            refresh_token = decrypt_token(row["refresh_token_ref"])
            refreshed = _simulate_token_refresh(provider, refresh_token)
            access_token = refreshed["access_token"]
            new_refresh = refreshed.get("refresh_token")

            from datetime import timedelta
            new_expires = (datetime.now(timezone.utc) + timedelta(seconds=refreshed["expires_in"])).isoformat()

            with get_connection() as conn:
                conn.execute(
                    """
                    UPDATE social_accounts
                    SET access_token_ref = ?, refresh_token_ref = ?,
                        token_expires_at = ?, status = 'connected', updated_at = ?
                    WHERE user_id = ? AND channel = ?
                    """,
                    (
                        encrypt_token(access_token),
                        encrypt_token(new_refresh) if new_refresh else row["refresh_token_ref"],
                        new_expires,
                        utc_now(),
                        user_id,
                        provider,
                    ),
                )
        except Exception as exc:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE social_accounts SET status = 'expired', updated_at = ? WHERE user_id = ? AND channel = ?",
                    (utc_now(), user_id, provider),
                )
            raise NotConnectedError(f"{provider} 토큰 갱신에 실패했습니다. 재연동이 필요합니다.") from exc

    return access_token
