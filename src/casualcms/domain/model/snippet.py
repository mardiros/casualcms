from datetime import datetime
from typing import Generic

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.model import Snippet_contra
from casualcms.utils import generate_id

uuid = str


class PublicMetadata(BaseModel):
    type: str = Field(...)


class Snippet(BaseModel, Generic[Snippet_contra]):

    id: uuid = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    snippet: Snippet_contra = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)

    class Meta:
        abstract = True

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    @property
    def key(self) -> str:
        return self.snippet.key

    @property
    def type(self) -> str:
        return self.snippet.__meta__.type

    @property
    def template(self) -> str:
        return self.snippet.__meta__.template

    @property
    def metadata(self) -> PublicMetadata:
        return PublicMetadata(type=self.type)
