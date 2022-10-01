from datetime import datetime
from typing import Any, Mapping

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.messages.commands import generate_id
from casualcms.domain.model.site import Site

uuid = str


class Page(BaseModel):
    id: uuid = Field(default_factory=generate_id, exclude=True)

    site: Site = Field(...)
    draft_id: str = Field(...)

    type: str = Field(...)
    template: str = Field(...)
    path: str = Field(...)

    title: str = Field(...)
    body: Mapping[str, Any] = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    @property
    def url(self) -> str:
        return f"{self.site.url}{self.path}"

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)
