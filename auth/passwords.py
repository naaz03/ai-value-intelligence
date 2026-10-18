"""Password hashing. PBKDF2-SHA256 — not reversible and not stored in plaintext."""

from __future__ import annotations

import hashlib
import hmac
import secrets

PASSWORD_ALGO = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 210_000
SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 8


def hash_password(password: str, salt_hex: str | None = None, iterations: int = PASSWORD_ITERATIONS) -> dict[str, str | int]:
    if not isinstance(password, str) or password == "":
        raise ValueError("Password is required.")
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return {
        "password_algo": PASSWORD_ALGO,
        "password_iterations": iterations,
        "password_salt": salt.hex(),
        "password_hash": digest.hex(),
    }


def verify_password(password: str, record: dict) -> bool:
    if not password or not record:
        return False
    stored = str(record.get("password_hash") or "")
    salt = str(record.get("password_salt") or "")
    try:
        iterations = int(record.get("password_iterations") or PASSWORD_ITERATIONS)
    except (TypeError, ValueError):
        return False
    if not stored or not salt:
        return False
    computed = hash_password(password, salt_hex=salt, iterations=iterations)
    return hmac.compare_digest(str(computed["password_hash"]), stored)


def validate_new_password(password: str, confirm: str, username: str | None = None) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if password != confirm:
        return "Password confirmation does not match."
    if username and password == username:
        return "Choose a password that is different from the username."
    return None
