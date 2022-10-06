import re
from typing import cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


class MissingBlockMetaError(Exception):
    ...


class BlockMeta(BaseModel):
    template: str = Field(...)
    title: str = Field(...)


class BlockMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        block_meta = None
        name = f"{namespace['__module__']}:{namespace['__qualname__']}"
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            block_meta = BlockMeta(
                template=getattr(meta, "template", ""),
                title=getattr(meta, "title", re.sub("([A-Z])", r" \g<0>", name)),
            )
            new_namespace["__meta__"] = block_meta
        else:
            raise MissingBlockMetaError(f"Meta class is missing for block {name}")
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        ret.__config__.title = block_meta.title  # type: ignore
        return ret


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    class Meta:
        ...
