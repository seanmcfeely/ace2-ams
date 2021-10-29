from pydantic import BaseModel, constr, EmailStr, Field, StrictBool, UUID4
from typing import List, Optional
from uuid import uuid4

from api.models import type_list_str, type_str, validators
from api.models.alert_queue import AlertQueueRead
from api.models.user_role import UserRoleRead


class UserBase(BaseModel):
    """Represents a user account within the application."""

    default_alert_queue: type_str = Field(
        description="The default alert queue the user will see on the alert management page"
    )

    display_name: type_str = Field(description="The user's full name")

    email: EmailStr = Field(description="The user's email address")

    enabled: StrictBool = Field(
        default=True, description="Whether or not the user account is enabled and can access the application"
    )

    roles: type_list_str = Field(description="A list of roles assigned to the user")

    timezone: type_str = Field(
        default="UTC", description="The timezone that will be used when the user views timestamps in the application"
    )

    username: type_str = Field(description="The username used to sign into the application")

    _validate_timezone: classmethod = validators.timezone("timezone")


class UserCreate(UserBase):
    password: constr(strict=True, min_length=8) = Field(description="The password to use for the user")

    uuid: UUID4 = Field(default_factory=uuid4, description="The UUID of the user")


class UserRead(UserBase):
    default_alert_queue: AlertQueueRead = Field(
        description="The default alert queue the user will see on the alert management page"
    )

    roles: List[UserRoleRead] = Field(description="A list of roles assigned to the user")

    uuid: UUID4 = Field(description="The UUID of the user")

    class Config:
        orm_mode = True


class UserUpdate(UserBase):
    default_alert_queue: Optional[type_str] = Field(
        description="The default alert queue the user will see on the alert management page"
    )

    display_name: Optional[type_str] = Field(description="The user's full name")

    email: Optional[EmailStr] = Field(description="The user's email address")

    enabled: Optional[StrictBool] = Field(
        description="Whether or not the user account is enabled and can access the application"
    )

    password: Optional[constr(strict=True, min_length=8)] = Field(description="The password to use for the user")

    roles: Optional[type_list_str] = Field(description="A list of roles assigned to the user")

    timezone: Optional[type_str] = Field(
        description="The timezone that will be used when the user views timestamps in the application"
    )

    username: Optional[type_str] = Field(description="The username used to sign into the application")

    _prevent_none: classmethod = validators.prevent_none(
        "default_alert_queue",
        "display_name",
        "email",
        "enabled",
        "password",
        "roles",
        "username",
    )
