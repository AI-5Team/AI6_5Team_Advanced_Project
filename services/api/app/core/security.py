from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import secrets

from app.core.config import get_settings


def _b64_encode(value: bytes) -> str:
    return urlsafe_b64encode(value).rstrip(b"=").decode("utf-8")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode((value + padding).encode("utf-8"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, expected = password_hash.split("$", 1)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000,
    ).hex()
    return hmac.compare_digest(digest, expected)


def create_access_token(user: dict) -> str:
    settings = get_settings()
    payload = {
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(seconds=settings.access_token_ttl_sec)).timestamp()
        ),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        settings.auth_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    return f"{_b64_encode(payload_bytes)}.{_b64_encode(signature)}"


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    payload_part, signature_part = token.split(".", 1)
    payload_bytes = _b64_decode(payload_part)
    expected_signature = hmac.new(
        settings.auth_secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).digest()
    signature = _b64_decode(signature_part)
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("invalid signature")
    payload = json.loads(payload_bytes.decode("utf-8"))
    if payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("token expired")
    return payload
