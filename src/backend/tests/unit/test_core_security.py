"""
Unit tests for app.core.security.

Security-critical code — these tests exercise the real bcrypt,
AES-256-GCM, HMAC-SHA256 and HS256 JWT primitives rather than
mocking them, and assert on real round-trip behaviour.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import string
from datetime import UTC, datetime, timedelta

import pytest
from cryptography.exceptions import InvalidTag
from jose import jwt

from app.core.security import (
    FieldEncryptor,
    create_access_token,
    create_refresh_token,
    generate_api_key,
    hash_password,
    verify_password,
    verify_token,
)

SECRET = "unit-test-secret-key-that-is-long-enough-32"
OTHER_SECRET = "a-completely-different-secret-key-32-chars"


def _make_key_b64(raw: bytes | None = None) -> str:
    """Base64-url encode a raw key (random 32 bytes by default)."""
    return base64.urlsafe_b64encode(raw or os.urandom(32)).decode("ascii")


@pytest.fixture
def encryptor() -> FieldEncryptor:
    """FieldEncryptor built on a fresh random 256-bit key."""
    return FieldEncryptor(_make_key_b64())


# ── Password hashing ───────────────────────────────────────


def test_hash_password_round_trip():
    """A password verifies against its own bcrypt hash."""
    hashed = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", hashed) is True


def test_hash_password_is_not_plaintext():
    """The hash never contains or equals the plaintext."""
    plain = "s3cr3t-passphrase"
    hashed = hash_password(plain)

    assert hashed != plain
    assert plain not in hashed


def test_hash_password_uses_bcrypt_cost_12():
    """The emitted hash advertises the 2b algorithm at cost 12."""
    hashed = hash_password("cost-check")

    assert hashed.startswith("$2b$12$")


def test_verify_password_rejects_wrong_password():
    """A different password does not verify."""
    hashed = hash_password("right-password")

    assert verify_password("wrong-password", hashed) is False


def test_verify_password_is_case_sensitive():
    """Password comparison is case sensitive."""
    hashed = hash_password("CaseSensitive")

    assert verify_password("casesensitive", hashed) is False
    assert verify_password("CaseSensitive", hashed) is True


def test_hash_password_salts_are_unique():
    """The same password hashed twice yields different digests."""
    first = hash_password("same-input")
    second = hash_password("same-input")

    assert first != second
    assert verify_password("same-input", first) is True
    assert verify_password("same-input", second) is True


def test_verify_password_handles_unicode():
    """Non-ASCII passwords round-trip through UTF-8 encoding."""
    plain = "pässwörd-Ω-秘密"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True
    assert verify_password("passwrd-O-secret", hashed) is False


# ── JWT creation ───────────────────────────────────────────


def test_create_access_token_payload_and_type():
    """Access tokens carry the caller data plus type=access."""
    token = create_access_token({"sub": "user-1"}, SECRET)

    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert decoded["sub"] == "user-1"
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_access_token_does_not_mutate_input():
    """The caller's dict is copied, not mutated."""
    data = {"sub": "user-1"}
    create_access_token(data, SECRET)

    assert data == {"sub": "user-1"}


def test_create_access_token_expiry_matches_argument():
    """exp lands within a second of now + expires_minutes."""
    before = datetime.now(UTC)
    token = create_access_token(
        {"sub": "user-1"}, SECRET, expires_minutes=15
    )

    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    exp = datetime.fromtimestamp(decoded["exp"], UTC)
    expected = before + timedelta(minutes=15)

    assert abs((exp - expected).total_seconds()) < 5


def test_create_refresh_token_type_and_expiry():
    """Refresh tokens are typed refresh and expire in days."""
    before = datetime.now(UTC)
    token = create_refresh_token(
        {"sub": "user-1"}, SECRET, expires_days=3
    )

    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    exp = datetime.fromtimestamp(decoded["exp"], UTC)

    assert decoded["type"] == "refresh"
    assert abs(
        (exp - (before + timedelta(days=3))).total_seconds()
    ) < 5


def test_access_and_refresh_tokens_differ():
    """The same claims produce distinct access/refresh tokens."""
    data = {"sub": "user-1", "tenant_id": "t-1"}

    assert create_access_token(data, SECRET) != create_refresh_token(
        data, SECRET
    )


# ── JWT verification ───────────────────────────────────────


def test_verify_token_returns_payload():
    """A freshly minted access token verifies and returns claims."""
    token = create_access_token(
        {"sub": "user-1", "roles": ["Admin"]}, SECRET
    )

    payload = verify_token(token, SECRET)

    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["roles"] == ["Admin"]


def test_verify_token_refresh_round_trip():
    """A refresh token verifies when expected_type=refresh."""
    token = create_refresh_token({"sub": "user-9"}, SECRET)

    payload = verify_token(token, SECRET, expected_type="refresh")

    assert payload is not None
    assert payload["sub"] == "user-9"


def test_verify_token_rejects_wrong_type():
    """An access token is rejected when a refresh is expected."""
    token = create_access_token({"sub": "user-1"}, SECRET)

    assert verify_token(token, SECRET, expected_type="refresh") is None


def test_verify_token_rejects_refresh_used_as_access():
    """A refresh token cannot be used as an access token."""
    token = create_refresh_token({"sub": "user-1"}, SECRET)

    assert verify_token(token, SECRET) is None


def test_verify_token_rejects_missing_type_claim():
    """A hand-rolled token without a type claim is rejected."""
    token = jwt.encode(
        {
            "sub": "user-1",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        SECRET,
        algorithm="HS256",
    )

    assert verify_token(token, SECRET) is None


def test_verify_token_rejects_wrong_secret():
    """A token signed with another key does not verify."""
    token = create_access_token({"sub": "user-1"}, SECRET)

    assert verify_token(token, OTHER_SECRET) is None


def test_verify_token_rejects_tampered_signature():
    """Flipping a signature byte invalidates the token."""
    token = create_access_token({"sub": "user-1"}, SECRET)
    head, payload, signature = token.split(".")
    # Mutate the FIRST signature character, not the last. A 32-byte
    # HMAC-SHA256 encodes to 43 base64url characters, and that final
    # character carries only 4 significant bits — the low 2 bits are
    # discarded on decode. Altering it therefore leaves the decoded
    # signature bytes unchanged roughly one run in sixteen, so the
    # token still verifies and the assertion below fails at random.
    # The first character always maps to real signature bits.
    flipped = "A" if signature[0] != "A" else "B"
    tampered = f"{head}.{payload}.{flipped}{signature[1:]}"

    assert tampered != token
    assert verify_token(tampered, SECRET) is None


def test_verify_token_rejects_tampered_payload():
    """Rewriting claims without re-signing is rejected."""
    token = create_access_token({"sub": "user-1"}, SECRET)
    head, payload, signature = token.split(".")

    raw = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    claims = json.loads(raw)
    claims["sub"] = "attacker"
    forged = (
        base64.urlsafe_b64encode(json.dumps(claims).encode())
        .decode()
        .rstrip("=")
    )
    tampered = f"{head}.{forged}.{signature}"

    assert verify_token(tampered, SECRET) is None


def test_verify_token_rejects_expired_token():
    """An already-expired token is rejected."""
    token = create_access_token(
        {"sub": "user-1"}, SECRET, expires_minutes=-1
    )

    assert verify_token(token, SECRET) is None


def test_verify_token_rejects_garbage():
    """A non-JWT string is rejected rather than raising."""
    assert verify_token("not-a-token", SECRET) is None
    assert verify_token("", SECRET) is None


def test_verify_token_rejects_alg_none_downgrade():
    """An unsigned alg=none token is not accepted as HS256."""
    header = (
        base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        )
        .decode()
        .rstrip("=")
    )
    claims = (
        base64.urlsafe_b64encode(
            json.dumps({"sub": "attacker", "type": "access"}).encode()
        )
        .decode()
        .rstrip("=")
    )

    assert verify_token(f"{header}.{claims}.", SECRET) is None


# ── FieldEncryptor construction ────────────────────────────


def test_field_encryptor_rejects_short_key():
    """A 16-byte key is refused."""
    with pytest.raises(ValueError, match="exactly 32 bytes"):
        FieldEncryptor(_make_key_b64(os.urandom(16)))


def test_field_encryptor_rejects_long_key():
    """A 64-byte key is refused."""
    with pytest.raises(ValueError, match="exactly 32 bytes"):
        FieldEncryptor(_make_key_b64(os.urandom(64)))


def test_field_encryptor_rejects_non_base64_key():
    """A key that is not valid base64 raises."""
    with pytest.raises((binascii.Error, ValueError)):
        FieldEncryptor("this is definitely not base64!!!")


def test_field_encryptor_accepts_exactly_32_bytes():
    """A 32-byte key constructs successfully."""
    enc = FieldEncryptor(_make_key_b64(b"\x01" * 32))

    assert enc.decrypt(enc.encrypt("ok")) == "ok"


# ── AES-256-GCM round trips ────────────────────────────────


def test_encrypt_decrypt_round_trip(encryptor):
    """decrypt(encrypt(x)) returns exactly x."""
    plain = "jane.doe@example.com"

    assert encryptor.decrypt(encryptor.encrypt(plain)) == plain


def test_encrypt_decrypt_unicode(encryptor):
    """Multi-byte UTF-8 survives the round trip."""
    plain = "Ünïcödé ✓ 秘密 — 🔐"

    assert encryptor.decrypt(encryptor.encrypt(plain)) == plain


def test_encrypt_decrypt_empty_string(encryptor):
    """An empty plaintext round-trips to an empty string."""
    assert encryptor.decrypt(encryptor.encrypt("")) == ""


def test_encrypt_decrypt_long_value(encryptor):
    """A large plaintext round-trips intact."""
    plain = "A" * 10_000

    assert encryptor.decrypt(encryptor.encrypt(plain)) == plain


def test_ciphertext_hides_plaintext(encryptor):
    """The ciphertext does not leak the plaintext."""
    plain = "sensitive-value"
    token = encryptor.encrypt(plain)

    assert plain not in token
    assert token != plain


def test_encrypt_uses_fresh_nonce(encryptor):
    """The same plaintext encrypts to different tokens."""
    first = encryptor.encrypt("same-input")
    second = encryptor.encrypt("same-input")

    assert first != second
    assert encryptor.decrypt(first) == "same-input"
    assert encryptor.decrypt(second) == "same-input"


def test_ciphertext_carries_12_byte_nonce_and_16_byte_tag(encryptor):
    """Token layout is nonce(12) + ciphertext + GCM tag(16)."""
    plain = "abcdefgh"
    raw = base64.urlsafe_b64decode(encryptor.encrypt(plain))

    assert len(raw) == 12 + len(plain.encode()) + 16


def test_decrypt_rejects_wrong_key():
    """A token from another key fails authentication."""
    enc_a = FieldEncryptor(_make_key_b64())
    enc_b = FieldEncryptor(_make_key_b64())
    token = enc_a.encrypt("top-secret")

    with pytest.raises(InvalidTag):
        enc_b.decrypt(token)


def test_decrypt_rejects_tampered_ciphertext(encryptor):
    """Flipping a ciphertext bit fails the GCM tag check."""
    raw = bytearray(base64.urlsafe_b64decode(encryptor.encrypt("value")))
    raw[-1] ^= 0x01
    tampered = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")

    with pytest.raises(InvalidTag):
        encryptor.decrypt(tampered)


def test_decrypt_rejects_tampered_nonce(encryptor):
    """Flipping a nonce bit fails the GCM tag check."""
    raw = bytearray(base64.urlsafe_b64decode(encryptor.encrypt("value")))
    raw[0] ^= 0xFF
    tampered = base64.urlsafe_b64encode(bytes(raw)).decode("ascii")

    with pytest.raises(InvalidTag):
        encryptor.decrypt(tampered)


def test_decrypt_rejects_truncated_token(encryptor):
    """A truncated bundle cannot be authenticated."""
    raw = base64.urlsafe_b64decode(encryptor.encrypt("value"))
    truncated = base64.urlsafe_b64encode(raw[:-4]).decode("ascii")

    with pytest.raises(InvalidTag):
        encryptor.decrypt(truncated)


def test_two_encryptors_with_same_key_interoperate():
    """A token encrypted by one instance decrypts in another."""
    key = _make_key_b64()
    token = FieldEncryptor(key).encrypt("shared-value")

    assert FieldEncryptor(key).decrypt(token) == "shared-value"


# ── HMAC lookup hashes ─────────────────────────────────────


def test_hmac_hash_is_deterministic(encryptor):
    """The same input always yields the same digest."""
    assert encryptor.hmac_hash("user@example.com") == encryptor.hmac_hash(
        "user@example.com"
    )


def test_hmac_hash_is_case_insensitive(encryptor):
    """Emails are lower-cased before hashing."""
    assert encryptor.hmac_hash("User@Example.COM") == encryptor.hmac_hash(
        "user@example.com"
    )


def test_hmac_hash_is_hex_sha256(encryptor):
    """The digest is 64 lowercase hex characters."""
    digest = encryptor.hmac_hash("user@example.com")

    assert len(digest) == 64
    assert set(digest) <= set(string.hexdigits.lower())


def test_hmac_hash_distinguishes_values(encryptor):
    """Different inputs produce different digests."""
    assert encryptor.hmac_hash("a@example.com") != encryptor.hmac_hash(
        "b@example.com"
    )


def test_hmac_hash_is_key_dependent():
    """The same input under different keys differs."""
    value = "user@example.com"
    a = FieldEncryptor(_make_key_b64()).hmac_hash(value)
    b = FieldEncryptor(_make_key_b64()).hmac_hash(value)

    assert a != b


def test_hmac_hash_matches_reference_implementation():
    """The digest equals HMAC-SHA256(raw_key, lower(value))."""
    raw = os.urandom(32)
    enc = FieldEncryptor(_make_key_b64(raw))
    expected = hmac.new(
        raw, b"user@example.com", hashlib.sha256
    ).hexdigest()

    assert enc.hmac_hash("USER@example.com") == expected


def test_hmac_hash_is_not_reversible(encryptor):
    """The digest does not contain the source value."""
    assert "user@example.com" not in encryptor.hmac_hash(
        "user@example.com"
    )


# ── API keys ───────────────────────────────────────────────


def test_generate_api_key_length():
    """token_urlsafe(32) yields a 43-character key."""
    assert len(generate_api_key()) == 43


def test_generate_api_key_is_url_safe():
    """Keys use only the URL-safe base64 alphabet."""
    allowed = set(string.ascii_letters + string.digits + "-_")

    assert set(generate_api_key()) <= allowed


def test_generate_api_key_is_unique():
    """Successive keys do not repeat."""
    keys = {generate_api_key() for _ in range(50)}

    assert len(keys) == 50
