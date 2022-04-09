from typing import Any, ClassVar, MutableMapping, Type

from pydantic import BaseModel, Field
from pydantic.config import BaseConfig

from casualcms.adapters.jinja2 import get_template

from .base import AbstractModel


class BasePageConfig(BaseConfig):
    template: str = ""


class AbstractPage(AbstractModel, BaseModel):
    Config = BasePageConfig
    __config__: ClassVar[Type[BasePageConfig]] = BasePageConfig

    def render(self) -> str:
        tpl = get_template(self.__config__.template)
        return tpl.render(**self.get_context())

    def get_context(self) -> MutableMapping[str, Any]:
        return self.dict()


class Page(AbstractPage):

    id: str = Field(...)
    slug: str = Field(...)
    title: str = Field(...)
