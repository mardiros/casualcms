from datetime import datetime
from typing import Generic

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.model.abstract_page import Page_contra
from casualcms.domain.model.site import Site
from casualcms.utils import generate_id

uuid = str


class PublishedPage(BaseModel, Generic[Page_contra]):
    id: uuid = Field(default_factory=generate_id, exclude=True)
    site: Site = Field(...)
    path: str = Field(...)
    draft_id: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)
    events: list[Event] = Field(default_factory=list, exclude=True)

    page: Page_contra = Field(...)

    @property
    def url(self) -> str:
        return f"{self.site.url}{self.path}"

    @property
    def type(self) -> str:
        return self.page.__meta__.type

    @property
    def title(self) -> str:
        return self.page.title

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)
