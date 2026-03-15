from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta

from passlib.context import CryptContext

from app.utils.time import now_utc

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

_SLUG_ALPHABET = string.ascii_letters + string.digits
_TTL_MAP = {
    "10m": timedelta(minutes=10),
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
    "1w": timedelta(weeks=1),
    "1m": timedelta(days=30),
}


def hash_secret(plain_value: str) -> str:
    return pwd_context.hash(plain_value)


def verify_secret(plain_value: str, hashed_value: str) -> bool:
    return pwd_context.verify(plain_value, hashed_value)


def generate_slug(length: int = 10) -> str:
    return "".join(secrets.choice(_SLUG_ALPHABET) for _ in range(length))


def parse_expiration(expires_in: str | None) -> datetime | None:
    if expires_in is None or expires_in == "never":
        return None
    ttl = _TTL_MAP.get(expires_in)
    if ttl is None:
        raise ValueError("invalid_expires_in")
    return now_utc() + ttl
