from typing import Generic, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

from casualcms.domain.model import Block

T = TypeVar("T")


class ListBlock(GenericModel, Block, Generic[T]):
    items: list[T] = Field(default_factory=list)

    class Meta:
        template = "atoms/list_block.jinja2"
