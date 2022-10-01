import enum
import re
from typing import Any, Set, Type, cast

from pydantic import BaseModel, ConstrainedStr, Field
from pydantic.main import ModelMetaclass
from result import Err, Ok, Result

SnippetType = Type["AbstractSnippet"]


class SnippetKey(ConstrainedStr):
    regex = re.compile("^[^/]+$")
    strip_whitespace = True


class SnippetError(enum.Enum):
    unregistered_type = "Unregistered type"


SnippetTypeResult = Result[SnippetType, SnippetError]


class SnippetTypeList:
    _types: dict[str, SnippetType] = {}

    def register(self, typ: SnippetType) -> None:
        self._types[typ.__meta__.type] = typ

    def resolve_type(self, typ: str) -> SnippetTypeResult:
        try:
            return Ok(self._types[typ])
        except KeyError:
            return Err(SnippetError.unregistered_type)

    @property
    def types(self) -> Set[SnippetType]:
        return set(self._types.values())


def list_snippet_types() -> Set[SnippetType]:
    return SnippetTypeList().types


def resolve_snippet_type(typ: str) -> SnippetTypeResult:
    return SnippetTypeList().resolve_type(typ)


class AbstractSnippetError(Exception):
    ...


class SnippetMeta(BaseModel):
    template: str = Field(...)
    abstract: bool = Field(...)
    type: str = Field(...)


class SnippetMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        snippet_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            snippet_meta = SnippetMeta(
                template=getattr(
                    meta,
                    "template",
                    "",  # TODO: a default template for users
                ),
                abstract=getattr(meta, "abstract", False),
                type=getattr(meta, "type", f"{namespace['__module__']}:{name}"),
            )
            new_namespace["__meta__"] = snippet_meta
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        if snippet_meta and not snippet_meta.abstract:
            SnippetTypeList().register(ret)  # type: ignore
        return ret


class AbstractSnippet(BaseModel, metaclass=SnippetMetaclass):
    __meta__: SnippetMeta

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractSnippetError(f"Snippet {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    def get_template(self) -> str:
        return self.__meta__.template
