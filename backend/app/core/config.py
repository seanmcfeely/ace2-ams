from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    jwt_algorithm: str
    jwt_expire_minutes: int
    jwt_secret: str


@lru_cache()
def get_settings():
    return Settings()
