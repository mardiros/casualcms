import re
from typing import Any, Dict, Sequence, cast

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass

from casualcms.domain.exceptions import MissingMetaError


class BlockMeta(BaseModel):
    template: str = Field(...)
    title: str = Field(...)


class BlockMetaclass(ModelMetaclass):
    def __new__(
        cls, name: str, bases: Sequence[type], namespace: Dict[str, Any], **kwargs: Any
    ) -> Any:
        new_namespace = {**namespace}
        block_meta = None
        short_name = name
        long_name = f"{namespace['__module__']}:{short_name}"
        meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
        elif bases:
            meta = getattr(bases[0], "Meta", None)  # generic

        if meta:
            block_meta = BlockMeta(
                template=getattr(meta, "template", ""),
                title=getattr(
                    meta,
                    "title",
                    re.sub("([A-Z])", r" \g<0>", short_name).strip(),
                ),
            )
            new_namespace["__meta__"] = block_meta
        else:
            raise MissingMetaError(long_name)
        ret = super().__new__(cls, name, bases, new_namespace, **kwargs)
        ret.__config__.title = block_meta.title  # type: ignore
        return ret


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    class Meta:
        ...


class GenericBlock(GenericModel, Block):
    """
    Block that use Generic such as ListBlock[T].


    class ListBlock(GenericBlock, Generic[T]):
        ...

    """

    class Meta:
        ...
