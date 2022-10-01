from datetime import datetime
from typing import Generic

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.messages.commands import generate_id
from casualcms.domain.model.abstract_page import PageImpl

uuid = str


class DraftPage(BaseModel, Generic[PageImpl]):

    id: uuid = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    page: PageImpl = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    @property
    def slug(self) -> str:
        return self.page.slug

    @property
    def path(self) -> str:
        return self.page.path

    @property
    def type(self) -> str:
        return self.page.__meta__.type

    @property
    def template(self) -> str:
        return self.page.__meta__.template

    @property
    def title(self) -> str:
        return self.page.title

    @property
    def description(self) -> str:
        return self.page.description
