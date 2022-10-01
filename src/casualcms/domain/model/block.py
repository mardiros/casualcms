from typing import cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass


class BlockMeta(BaseModel):
    template: str = Field(...)
    type: str = Field(...)


class BlockMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        page_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            page_meta = BlockMeta(
                template=getattr(
                    meta,
                    "template",
                    "",  # TODO: a default template for users
                ),
                type=getattr(meta, "type", f"{namespace['__module__']}:{name}"),
            )
            new_namespace["__meta__"] = page_meta
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        return ret


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    def get_template(self) -> str:
        return self.__meta__.template
