from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    database_url: PostgresDsn
    jwt_algorithm: str
    jwt_expire_seconds: int
    jwt_secret: str


def get_settings():
    return Settings()
