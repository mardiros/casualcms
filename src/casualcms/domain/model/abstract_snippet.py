import enum
import re
from typing import Any, Mapping, Set, Type, TypeVar, cast

from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass
from result import Err, Ok, Result

from casualcms.domain.exceptions import MissingMetaError
from casualcms.domain.model.abstract import BaseUIModel
from casualcms.domain.model.fields import SlugField

SnippetType = Type["AbstractSnippet"]


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
    title: str = Field(...)


class SnippetMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        short_name = f"{namespace['__qualname__']}"
        long_name = f"{namespace['__module__']}:{short_name}"
        snippet_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            type_ = getattr(meta, "type", long_name)
            snippet_meta = SnippetMeta(
                template=getattr(meta, "template", ""),
                abstract=getattr(meta, "abstract", False),
                type=type_,
                title=getattr(
                    meta,
                    "title",
                    re.sub("([A-Z])", r" \g<0>", short_name).strip(),
                ),
            )
            new_namespace["__meta__"] = snippet_meta
        else:
            raise MissingMetaError(long_name)
        ret = super().__new__(  # type: ignore
            mcls, name, bases, new_namespace, **kwargs  # type: ignore
        )
        if snippet_meta and not snippet_meta.abstract:
            ret.model_config["title"] = snippet_meta.title  # type: ignore
            SnippetTypeList().register(ret)  # type: ignore
        return ret  # type: ignore


class AbstractSnippet(BaseUIModel, metaclass=SnippetMetaclass):
    __meta__: SnippetMeta

    key: SlugField = Field(...)

    class Meta:
        abstract = True

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractSnippetError(f"Snippet {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    @property
    def metadata(self) -> Mapping[str, Any]:
        return {
            "type": self.__meta__.type,
        }

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.model_fields.items():
            ret[key] = cls.get_widget(key, val)
        return ret


Snippet_contra = TypeVar("Snippet_contra", bound=AbstractSnippet, contravariant=True)
