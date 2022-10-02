from typing import cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


class MissingBlockMetaError(Exception):
    ...


class BlockMeta(BaseModel):
    template: str = Field(...)


class BlockMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        block_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            block_meta = BlockMeta(
                template=getattr(meta, "template", ""),
            )
            new_namespace["__meta__"] = block_meta
        else:
            name = f"{namespace['__module__']}:{namespace['__qualname__']}"
            raise MissingBlockMetaError(f"Meta class is missing for block {name}")
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        return ret


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    class Meta:
        ...
