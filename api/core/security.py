"""Password hashing and email OTP helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash

from api.core.config import settings

password_hash = PasswordHash.recommended()

OTP_LENGTH = 6
OTP_ALPHABET = "0123456789"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if not hashed_password:
        return False
    return password_hash.verify(plain_password, hashed_password)


def validate_password_strength(password: str) -> str | None:
    """Return an error message if the password is too weak, else None."""
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters."
    if password.isspace() or not password.strip():
        return "Password cannot be blank."
    if len(password.encode("utf-8")) > 1024:
        return "Password is too long."
    return None


def generate_otp(length: int = OTP_LENGTH) -> str:
    return "".join(secrets.choice(OTP_ALPHABET) for _ in range(length))


def hash_otp(otp: str, email: str) -> str:
    """HMAC-SHA256 of the OTP keyed by SECRET_KEY, bound to normalized email."""
    message = f"{email.strip().lower()}:{otp}".encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def verify_otp(otp: str, email: str, otp_hash: str | None) -> bool:
    if not otp_hash:
        return False
    candidate = hash_otp(otp, email)
    return hmac.compare_digest(candidate, otp_hash)


def otp_expiry(now: datetime | None = None) -> datetime:
    base = now or datetime.now(tz=timezone.utc)
    return base + timedelta(minutes=settings.EMAIL_OTP_EXPIRE_MINUTES)
