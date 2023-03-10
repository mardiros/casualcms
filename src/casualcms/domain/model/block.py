import re
from typing import Any, Dict, Literal, Sequence, cast

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass
from pygments.formatters import HtmlFormatter

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
        ret = super().__new__(cls, name, bases, new_namespace, **kwargs)  # type: ignore
        ret.__config__.title = block_meta.title  # type: ignore
        return ret  # type: ignore


class Block(BaseModel, metaclass=BlockMetaclass):
    __meta__: BlockMeta

    class Meta:
        ...


class CodeBlockMeta(BlockMeta):
    formatter: HtmlFormatter = Field(...)  # type: ignore

    class Config:
        arbitrary_types_allowed = True


class CodeBlockMetaclass(BlockMetaclass):
    def __new__(
        cls, name: str, bases: Sequence[type], namespace: Dict[str, Any], **kwargs: Any
    ) -> Any:
        ret = super().__new__(cls, name, bases, namespace, **kwargs)  # type: ignore
        meta: CodeBlockMeta = getattr(ret, "__meta__")

        meta_ns = None
        if "Meta" in namespace:
            meta_ns = cast(object, namespace.pop("Meta"))
        elif bases:
            meta_ns = getattr(bases[0], "Meta", None)  # generic

        setattr(
            ret,
            "__meta__",
            CodeBlockMeta(
                template=meta.template,
                title=meta.title,
                formatter=getattr(
                    meta_ns,
                    "formatter",
                    HtmlFormatter(),  # type: ignore
                ),
            ),
        )
        return ret  # type: ignore


class CodeBlock(Block, metaclass=CodeBlockMetaclass):
    """Code block to render code with pygment"""

    language: Literal[
        "Bash",
        "Go",
        "Java",
        "JavaScript",
        "Python",
        "Ruby",
        "Rust",
        "SQL",
        "Typescript",
    ] = Field(widget="select")
    code: str = Field(widget="textarea")


class GenericBlock(GenericModel, Block):
    """
    Block that use Generic such as ListBlock[T].


    class ListBlock(GenericBlock, Generic[T]):
        ...

    """

    class Meta:
        ...
