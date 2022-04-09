from types import NoneType
from typing import Any, ClassVar, MutableMapping, Optional, Type

from pydantic import BaseModel, Field
from pydantic.config import BaseConfig

from .base import AbstractModel


class BasePageConfig(BaseConfig):
    template: str = ""


class AbstractPage(AbstractModel, BaseModel):
    Config = BasePageConfig
    __config__: ClassVar[Type[BasePageConfig]] = BasePageConfig

    def get_context(self) -> MutableMapping[str, Any]:
        return self.dict()


class Page(AbstractPage):

    id: str = Field(...)
    slug: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)

    parent: Optional["Page"] = None

    @property
    def path(self):
        slugs = []
        page = self
        while page:
            slugs.append(page.slug)
            page = page.parent
        return "/".join(reversed(slugs)) or "/"
