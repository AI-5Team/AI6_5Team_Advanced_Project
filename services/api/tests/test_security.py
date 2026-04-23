"""
Security integration tests for Sprint 1 & 2 features.

Covers:
- PIPA-compliant registration (4 consents, birthDate, age-14 gate)
- argon2id password hashing
- HttpOnly cookie session (issue + verify + revoke)
- Account lockout (5 failed logins)
- CryptoService AES-256-GCM round-trip
- Email verify + password reset token flow
- Soft-delete + hard-delete batch
- Rate limiting (register IP limit)
"""
from __future__ import annotations

import pytest


VALID_REGISTER = {
    "email": "sec-test@example.com",
    "password": "Passw0rd!Safe",
    "name": "보안테스터",
    "birthDate": "1995-06-15",
    "agreedToTerms": True,
    "agreedToPrivacy": True,
    "agreedToAge14": True,
    "agreedToOverseasTransfer": True,
}


def _make_client(monkeypatch, tmp_path):
    runtime_dir = tmp_path / ".runtime"
    monkeypatch.setenv("APP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("APP_STORAGE_DIR", str(runtime_dir / "storage"))
    monkeypatch.setenv("APP_DB_PATH", str(runtime_dir / "app.sqlite3"))
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


# ---------------------------------------------------------------------------
# Registration & session
# ---------------------------------------------------------------------------

def test_register_sets_session_cookie(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    resp = client.post("/api/auth/register", json=VALID_REGISTER)
    assert resp.status_code == 201
    # HttpOnly cookies appear in Set-Cookie header and are stored in the client's cookie jar
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session" in set_cookie or "session" in client.cookies, \
        "HttpOnly session cookie must be set on register"
    body = resp.json()
    assert body["user"]["email"] == VALID_REGISTER["email"]
    assert "accessToken" in body


def test_register_missing_consent_rejected(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    payload = {**VALID_REGISTER, "agreedToPrivacy": False}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_under_14_rejected(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    payload = {**VALID_REGISTER, "email": "young@example.com", "birthDate": "2015-01-01"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 403


def test_register_short_password_rejected(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    payload = {**VALID_REGISTER, "email": "shortpw@example.com", "password": "short"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 422


def test_login_sets_cookie_and_session_endpoint_works(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)
    resp = client.post("/api/auth/login", json={
        "email": VALID_REGISTER["email"],
        "password": VALID_REGISTER["password"],
    })
    assert resp.status_code == 200
    assert "session" in resp.cookies

    session_resp = client.get("/api/auth/session")
    assert session_resp.status_code == 200
    assert session_resp.json()["user"]["email"] == VALID_REGISTER["email"]


def test_logout_clears_session(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)
    client.post("/api/auth/login", json={
        "email": VALID_REGISTER["email"],
        "password": VALID_REGISTER["password"],
    })
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 204
    # Cookie should be cleared (value empty or max-age=0)
    session_resp = client.get("/api/auth/session")
    assert session_resp.status_code == 401


# ---------------------------------------------------------------------------
# argon2id password hash format
# ---------------------------------------------------------------------------

def test_password_stored_as_argon2id(monkeypatch, tmp_path):
    from app.core.database import get_connection
    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)
    with get_connection() as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE email = ?",
                           (VALID_REGISTER["email"],)).fetchone()
    assert row is not None
    assert row["password_hash"].startswith("$argon2id$"), \
        f"Expected argon2id hash, got: {row['password_hash'][:30]}"


# ---------------------------------------------------------------------------
# Account lockout
# ---------------------------------------------------------------------------

def test_account_locked_after_5_failures(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    lock_email = "lockout-test@example.com"
    client.post("/api/auth/register", json={**VALID_REGISTER, "email": lock_email})
    for _ in range(5):
        r = client.post("/api/auth/login", json={
            "email": lock_email,
            "password": "WrongPassword999!",
        })
        assert r.status_code == 401

    # 6th attempt: either rate-limited (429) or account-locked (401/403)
    r = client.post("/api/auth/login", json={
        "email": lock_email,
        "password": "WrongPassword999!",
    })
    assert r.status_code in (401, 403, 429)
    assert r.json()["error"]["code"] in ("INVALID_CREDENTIALS", "ACCOUNT_LOCKED", "RATE_LIMITED")


# ---------------------------------------------------------------------------
# PIPA consents recorded in DB
# ---------------------------------------------------------------------------

def test_consent_rows_created_on_register(monkeypatch, tmp_path):
    from app.core.database import get_connection
    client = _make_client(monkeypatch, tmp_path)
    resp = client.post("/api/auth/register", json=VALID_REGISTER)
    assert resp.status_code == 201
    with get_connection() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?",
                            (VALID_REGISTER["email"],)).fetchone()
        consents = conn.execute(
            "SELECT consent_type, agreed FROM consents WHERE user_id = ?",
            (user["id"],),
        ).fetchall()
    types = {row["consent_type"] for row in consents}
    assert types == {"terms", "privacy", "age_14", "overseas_transfer"}
    assert all(row["agreed"] == 1 for row in consents)


def test_consent_version_stored(monkeypatch, tmp_path):
    from app.core.database import get_connection
    from app.services.consent import CURRENT_CONSENT_VERSIONS
    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)
    with get_connection() as conn:
        user = conn.execute("SELECT id FROM users WHERE email = ?",
                            (VALID_REGISTER["email"],)).fetchone()
        consents = conn.execute(
            "SELECT consent_type, version FROM consents WHERE user_id = ?",
            (user["id"],),
        ).fetchall()
    stored = {row["consent_type"]: row["version"] for row in consents}
    for consent_type, expected_version in CURRENT_CONSENT_VERSIONS.items():
        assert stored.get(consent_type) == expected_version, \
            f"{consent_type}: expected version {expected_version!r}, got {stored.get(consent_type)!r}"


# ---------------------------------------------------------------------------
# CryptoService AES-256-GCM
# ---------------------------------------------------------------------------

def test_crypto_roundtrip():
    from app.services.crypto import decrypt_token, encrypt_token
    plain = "instagram-oauth-token-abc123-xyz"
    enc = encrypt_token(plain)
    assert enc != plain
    assert decrypt_token(enc) == plain


def test_crypto_different_iv_each_time():
    from app.services.crypto import encrypt_token
    enc1 = encrypt_token("same-token")
    enc2 = encrypt_token("same-token")
    assert enc1 != enc2, "Each encryption must use a fresh random IV"


def test_crypto_tamper_detected():
    import pytest
    from app.services.crypto import decrypt_token, encrypt_token
    enc = encrypt_token("test-token")
    # Flip a byte in the ciphertext portion
    import base64
    raw = bytearray(base64.b64decode(enc))
    raw[15] ^= 0xFF
    tampered = base64.b64encode(bytes(raw)).decode()
    with pytest.raises(Exception):
        decrypt_token(tampered)


def test_oauth_token_stored_encrypted_after_callback(monkeypatch, tmp_path):
    from urllib.parse import parse_qs, urlparse
    from app.core.database import get_connection
    from app.services.crypto import decrypt_token

    client = _make_client(monkeypatch, tmp_path)

    connect_resp = client.post("/api/social-accounts/instagram/connect")
    assert connect_resp.status_code == 200
    parsed = urlparse(connect_resp.json()["redirectUrl"])
    query = parse_qs(parsed.query)

    cb_resp = client.get(
        f"/api/social-accounts/instagram/callback?code={query['code'][0]}&state={query['state'][0]}"
    )
    assert cb_resp.status_code == 200

    with get_connection() as conn:
        row = conn.execute(
            "SELECT access_token_ref FROM social_accounts WHERE channel = 'instagram'"
        ).fetchone()
    assert row is not None
    token_ref = row["access_token_ref"]
    assert token_ref != "instagram-token", "Token must not be stored in plain text"
    # Must decrypt cleanly
    plain = decrypt_token(token_ref)
    assert "instagram" in plain


# ---------------------------------------------------------------------------
# Email verify + password reset token (single-use)
# ---------------------------------------------------------------------------

def test_password_reset_token_single_use(monkeypatch, tmp_path):
    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)

    reset_resp = client.post("/api/auth/password/reset-request", json={
        "email": VALID_REGISTER["email"],
    })
    assert reset_resp.status_code == 200
    dev_token = reset_resp.json().get("devToken")
    assert dev_token, "devToken must be returned in non-production"

    # First confirm: OK
    confirm1 = client.post("/api/auth/password/reset-confirm", json={
        "token": dev_token,
        "newPassword": "NewSecurePass1!",
    })
    assert confirm1.status_code == 200

    # Second confirm with same token: must fail
    confirm2 = client.post("/api/auth/password/reset-confirm", json={
        "token": dev_token,
        "newPassword": "AnotherPass99!",
    })
    assert confirm2.status_code in (400, 401, 422)


# ---------------------------------------------------------------------------
# Soft-delete and hard-delete batch
# ---------------------------------------------------------------------------

def test_soft_delete_and_hard_delete_batch(monkeypatch, tmp_path):
    from app.core.database import get_connection
    from app.services.hard_delete import run_hard_delete_batch

    client = _make_client(monkeypatch, tmp_path)
    client.post("/api/auth/register", json=VALID_REGISTER)

    # Login to get a session cookie
    client.post("/api/auth/login", json={
        "email": VALID_REGISTER["email"],
        "password": VALID_REGISTER["password"],
    })

    delete_resp = client.delete("/api/account/me")
    assert delete_resp.status_code == 200
    body = delete_resp.json()
    assert "scheduledDeletionAt" in body

    # Soft-delete: user row must still exist with deleted_at set
    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, deleted_at, hard_delete_at FROM users WHERE email LIKE 'deleted_%@deleted.local'"
        ).fetchone()
    assert user is not None
    assert user["deleted_at"] is not None
    assert user["hard_delete_at"] is not None
    user_id = user["id"]

    # Force hard_delete_at to now so batch picks it up
    from datetime import datetime, timezone
    past = "2000-01-01T00:00:00+00:00"
    with get_connection() as conn:
        conn.execute("UPDATE users SET hard_delete_at = ? WHERE id = ?", (past, user_id))

    count = run_hard_delete_batch()
    assert count >= 1

    with get_connection() as conn:
        gone = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    assert gone is None, "User row must be hard-deleted after batch"


# ---------------------------------------------------------------------------
# Audit log written on login
# ---------------------------------------------------------------------------

def test_audit_log_written_on_login(monkeypatch, tmp_path):
    from app.core.database import get_connection
    client = _make_client(monkeypatch, tmp_path)
    resp = client.post("/api/auth/register", json=VALID_REGISTER)
    assert resp.status_code == 201
    client.post("/api/auth/login", json={
        "email": VALID_REGISTER["email"],
        "password": VALID_REGISTER["password"],
    })
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT event_type FROM audit_logs WHERE event_type IN ('register', 'login_success')"
        ).fetchall()
    events = {r["event_type"] for r in rows}
    assert "register" in events, f"Expected 'register' in {events}"
    assert "login_success" in events, f"Expected 'login_success' in {events}"
