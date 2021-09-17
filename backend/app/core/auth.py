from collections.abc import Mapping
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, jwt, JWTError
from passlib.hash import bcrypt_sha256

from core.config import get_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")


def _create_token(token_type: str, lifetime: timedelta, sub: str) -> str:
    """
    Generic function to generate and return a JWT.

    Args:
        token_type: "access_token" or "refresh_token"
        lifetime: a datetime timedelta representing how long the token should remain valid
        sub: the subject to use for the token claims (username by default)
    """

    payload = {
        "type": token_type,
        "exp": datetime.utcnow() + lifetime,
        "iat": datetime.utcnow(),
        "sub": sub,
    }

    return jwt.encode(payload, get_settings().jwt_secret, algorithm=get_settings().jwt_algorithm)


def create_access_token(sub: str) -> str:
    """
    Generates and returns an access_token JWT that is used to authenticate to the API endpoints.

    Args:
        sub: the subject to use for the token claims (username by default)
    """

    return _create_token(
        token_type="access_token",
        lifetime=timedelta(seconds=get_settings().jwt_access_expire_seconds),
        sub=sub,
    )


def create_refresh_token(sub: str) -> str:
    """
    Generates and returns a refresh_token JWT that is used to obtain a new access_token.

    Args:
        sub: the subject to use for the token claims (username by default)
    """

    return _create_token(
        token_type="refresh_token",
        lifetime=timedelta(seconds=get_settings().jwt_refresh_expire_seconds),
        sub=sub,
    )


def decode_token(token: str) -> Mapping:
    """
    Decodes the JWT and returns its claims.

    Args:
        token: an access_token or refresh_token
    """

    return jwt.decode(token, get_settings().jwt_secret, algorithms=[get_settings().jwt_algorithm])


def hash_password(password: str) -> str:
    """
    Salts and hashes the given password.

    Args:
        password: the plaintext password to hash
    """

    return bcrypt_sha256.hash(password)


def refresh_token(refresh_token: str = Depends(oauth2_scheme)) -> str:
    """
    Generates and returns a new access_token if the given refresh_token is valid and not expired.

    This is designed to be used with FastAPI dependency injection so that the token is validated before the refresh auth
    API endpoint is invoked.

    Args:
        refresh_token: a valid refresh_token

    Returns:
        a new access_token
    """

    def _is_refresh_token(claims: dict) -> bool:
        return claims["type"] == "refresh_token"

    try:
        claims = decode_token(refresh_token)

        if _is_refresh_token(claims):
            return create_access_token(claims["sub"])

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_access_token(access_token: str = Depends(oauth2_scheme)) -> str:
    """
    Validates that the given access_token can be decoded using our secret key, that it is not expired, and
    that it is in fact an access_token and not another type of token.

    This is designed to be used with FastAPI dependency injection so that the token is validated before the API
    endpoints are invoked.

    Args:
        access_token: a valid access_token

    Returns:
        a string representing the "sub" claim from the token (the username by default)
    """

    def _is_access_token(claims: dict) -> bool:
        return claims["type"] == "access_token"

    try:
        claims = decode_token(access_token)

        if _is_access_token(claims):
            return claims["sub"]

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies that the given password matches the given hashed password.

    Args:
        password: the plaintext password
        hashed_password: the hashed password used to verify the plaintext password
    """

    return bcrypt_sha256.verify(password, hashed_password)
