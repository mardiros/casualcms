from datetime import datetime
from typing import Generic

from pydantic import BaseModel, Field

from casualcms.domain.messages import Event
from casualcms.domain.model.abstract_page import AbstractPage, Page_contra
from casualcms.utils import generate_id

uuid = str


class BreadCrumbItem(BaseModel):
    """Metadata exposed to the API"""

    slug: str
    path: str
    title: str


class PublicMetadata(BaseModel):
    """Metadata exposed to the API"""

    breadcrumb: list[BreadCrumbItem]
    type: str
    path: str


class DraftPage(BaseModel, Generic[Page_contra]):

    id: uuid = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    page: Page_contra = Field(...)

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

    @property
    def metadata(self) -> PublicMetadata:
        breadcrumb: list[BreadCrumbItem] = []
        p: AbstractPage = self.page
        while True:
            breadcrumb.append(
                BreadCrumbItem(
                    slug=p.slug,
                    path=p.path,
                    title=p.title,
                ),
            )
            if p.parent is None:
                break
            p = p.parent
        return PublicMetadata(
            type=self.type,
            path=self.path,
            breadcrumb=list(reversed(breadcrumb)),
        )
