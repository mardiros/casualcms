from datetime import datetime

from pydantic import BaseModel, Field

from casualcms.domain.messages.base import Event

uuid = str


class Site(BaseModel):
    id: uuid = Field(..., description="Unique identifier of the website")
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)
    draft_id: uuid | None = Field(
        ..., description="Root page id, None only for creational purpose"
    )
    hostname: str = Field(..., description="hostname of this website")
    root_page_path: str = Field(..., description="Root page path")
    default: bool = Field(..., description="Is the default site")
    secure: bool = Field(
        ..., description="True means that the site use https, not http"
    )
    events: list[Event] = Field(default_factory=list, exclude=True)

    def __hash__(self) -> int:
        return hash(self.id)  # type: ignore
