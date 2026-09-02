"""
Security utilities — passwords, JWTs, field-level encryption, API keys.

AES-256-GCM for PII encryption; bcrypt (cost 12) for passwords;
HS256 JWTs for stateless auth; HMAC-SHA256 for encrypted-field lookups.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt

from app.core.logging import get_logger

logger = get_logger(__name__)

_GCM_NONCE_BYTES = 12


# ---------------------------------------------------------------------------
# Password hashing (bcrypt, cost factor 12)
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt cost factor 12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# JWT creation and verification
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_minutes: int = 30,
) -> str:
    """Issue a short-lived JWT access token."""
    payload = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_refresh_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_days: int = 7,
) -> str:
    """Issue a longer-lived JWT refresh token."""
    payload = data.copy()
    expire = datetime.now(UTC) + timedelta(days=expires_days)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def verify_token(
    token: str,
    secret_key: str,
    algorithm: str = "HS256",
    expected_type: str = "access",
) -> dict | None:
    """
    Decode and validate a JWT.

    Returns the payload dict on success, None on any failure.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        if payload.get("type") != expected_type:
            return None
        return payload
    except JWTError:
        logger.warning("jwt_verification_failed")
        return None


# ---------------------------------------------------------------------------
# AES-256-GCM field-level encryption for PII
# ---------------------------------------------------------------------------


class FieldEncryptor:
    """Encrypt / decrypt individual field values with AES-256-GCM."""

    def __init__(self, key_b64: str) -> None:
        raw_key = base64.urlsafe_b64decode(key_b64)
        if len(raw_key) != 32:
            raise ValueError("ENCRYPTION_KEY must decode to exactly 32 bytes")
        self._aesgcm = AESGCM(raw_key)
        self._hmac_key = raw_key  # reuse for HMAC lookups

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext, returning base64(nonce + ciphertext)."""
        nonce = os.urandom(_GCM_NONCE_BYTES)
        ciphertext = self._aesgcm.encrypt(
            nonce, plaintext.encode("utf-8"), None
        )
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Decrypt a base64-encoded nonce+ciphertext bundle."""
        raw = base64.urlsafe_b64decode(token)
        nonce = raw[:_GCM_NONCE_BYTES]
        ciphertext = raw[_GCM_NONCE_BYTES:]
        plaintext_bytes = self._aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext_bytes.decode("utf-8")

    def hmac_hash(self, value: str) -> str:
        """
        Deterministic HMAC-SHA256 for encrypted-field lookups.

        Allows WHERE email_hash = ? without decrypting every row.
        """
        return hmac.new(
            self._hmac_key,
            value.lower().encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()


# ---------------------------------------------------------------------------
# API key generation
# ---------------------------------------------------------------------------


def generate_api_key() -> str:
    """Generate a cryptographically secure API key (43 chars)."""
    return secrets.token_urlsafe(32)
