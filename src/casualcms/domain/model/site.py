from datetime import datetime
from pydantic import BaseModel, Field

from casualcms.domain.messages.base import Event

uuid = str


class Site(BaseModel):
    id: uuid = Field(..., description="Unique identifier of the website")
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)
    page_id: uuid = Field(..., description="Root page id")
    hostname: str = Field(..., description="hostname of this website")
    root: str = Field(..., description="Root page path")
    default: bool = Field(..., description="Is the default site")
    events: list[Event] = Field(default_factory=list, exclude=True)
