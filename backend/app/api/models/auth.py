from pydantic import BaseModel, Field

from api.models import type_str


class AuthBase(BaseModel):
    """Represents the data needed to authenticate with the backend."""

    username: type_str = Field()

    password: type_str = Field()
