import re
from typing import cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.domain.exceptions import MissingMetaError


class BlockMeta(BaseModel):
    template: str = Field(...)
    title: str = Field(...)


class BlockMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        block_meta = None
        short_name = f"{namespace['__qualname__']}"
        long_name = f"{namespace['__module__']}:{short_name}"
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
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
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        ret.__config__.title = block_meta.title  # type: ignore
        return ret


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    class Meta:
        ...
