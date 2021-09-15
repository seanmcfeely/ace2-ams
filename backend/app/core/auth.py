from collections.abc import Mapping
from datetime import datetime, timedelta
from jose import jwt
from passlib.hash import bcrypt_sha256

from core.config import get_settings


def _create_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    payload = {
        "type": token_type,
        "exp": datetime.utcnow() + lifetime,
        "iat": datetime.utcnow(),
        "sub": sub,
    }

    return jwt.encode(payload, get_settings().jwt_secret, algorithm=get_settings().jwt_algorithm)


def create_access_token(sub: str) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(seconds=get_settings().jwt_expire_seconds),
        sub=sub,
    )


def decode_token(token: str) -> Mapping:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=[get_settings().jwt_algorithm])


def hash_password(password: str) -> str:
    return bcrypt_sha256.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt_sha256.verify(password, hashed_password)
