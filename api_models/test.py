from pydantic import BaseModel, Field
from typing import Optional

from api_models import type_str


class AddTestAlert(BaseModel):
    template: str = Field(description="The name of the alert template inside of backend/app/tests/alerts/ to insert")

    count: int = Field(description="The number of copies of the alert template to insert")

    delay: int = Field(
        default=0,
        description="The number of seconds to wait between inserting each alert so their timestamps are different",
    )


class AddTestEvent(BaseModel):
    alert_template: str = Field(
        description="The name of the alert template inside of backend/app/tests/alerts/ to insert"
    )

    alert_count: int = Field(description="The number of copies of the alert template to insert")

    delay: int = Field(
        default=0,
        description="The number of seconds to wait between inserting each alert so their timestamps are different",
    )

    name: str = Field(description="The name to use for the event")

    queue: str = Field(description="The queue to use for the event", default="external")

    status: Optional[type_str] = Field(description="The status to use for the event", default="OPEN")
