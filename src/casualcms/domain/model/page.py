from datetime import datetime
from typing import Any, MutableMapping, Optional

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.domain.messages import Event

from .base import AbstractModel


class PageMeta(BaseModel):
    template: str = Field(...)


class PageMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        if "Meta" in namespace:
            page_meta = PageMeta(
                template=getattr(
                    namespace["Meta"],  # type: ignore
                    "template",
                    "",  # TODO: a default template for users
                )
            )
            new_namespace["__meta__"] = page_meta
        return super().__new__(mcls, name, bases, new_namespace, **kwargs)


class AbstractPage(AbstractModel, BaseModel, metaclass=PageMetaclass):
    __meta__: PageMeta

    def get_context(self) -> MutableMapping[str, Any]:
        return self.dict(exclude={"events", "created_at"})

    def get_template(self) -> str:
        return self.__meta__.template


class Page(AbstractPage):

    id: str = Field(...)
    slug: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)

    parent: Optional["Page"] = Field(default_factory=list, exclude=True)
    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    @property
    def path(self) -> str:
        slugs = []
        page: Optional["Page"] = self
        while page:
            slugs.append(page.slug)
            page = page.parent
        return "/".join(reversed(slugs)) or "/"

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)
