from collections.abc import Mapping
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, jwt, JWTError
from passlib.hash import bcrypt_sha256

from core.config import get_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def validate_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)

        # Make sure this is an access_token and not another type such as a refresh_token
        if payload["type"] == "access_token":
            return payload["sub"]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt_sha256.verify(password, hashed_password)
