from pydantic import BaseModel

from api.models import type_str


class Token(BaseModel):
    """Represents a JWT used to authenticate with the API."""

    access_token: type_str

    token_type: type_str
