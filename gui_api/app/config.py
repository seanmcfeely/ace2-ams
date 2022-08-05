import random
import string

from pydantic import BaseSettings, Field


def _get_random_string(length: int):
    return "".join(random.SystemRandom().choice(string.printable) for _ in range(length))


JWT_SECRET = None
if JWT_SECRET is None:
    JWT_SECRET = _get_random_string(64)


class Settings(BaseSettings):
    """
    Reads OS environment variables and maps them into attributes using Pydantic
    """

    cookies_samesite: str = Field(default="lax")
    cookies_secure: bool = Field(default=True)
    database_api_url: str
    jwt_access_expire_seconds: int = Field(default=900)
    jwt_algorithm: str = Field(default="HS256")
    jwt_refresh_expire_seconds: int = Field(default=43200)
    jwt_secret: str = Field(default=JWT_SECRET)


def get_settings():
    """
    Helper function to read the settings. Can be patched for unit testing.
    """

    return Settings()
