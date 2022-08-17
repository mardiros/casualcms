from datetime import datetime
from typing import Any, MutableMapping, Type, cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.domain.messages import Event
from casualcms.domain.messages.commands import generate_id

uuid = str
SnippetType = Type["Snippet"]


class UnregisterType(Exception):
    def __init__(self, typ: str) -> None:
        super().__init__(f"Unregistered type {typ}")


class SnippetTypeList:
    _types: dict[str, SnippetType] = {}

    def register(self, typ: SnippetType) -> None:
        self._types[typ.__meta__.type] = typ

    def resolve_type(self, typ: str) -> SnippetType:
        try:
            return self._types[typ]
        except KeyError:
            raise UnregisterType(typ)


def resolve_snippet_type(typ: str) -> SnippetType:
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


class Snippet(AbstractSnippet):

    id: uuid = Field(default_factory=generate_id, exclude=True)
    slug: str = Field(...)

    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    class Meta:
        abstract = True

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    def get_data_context(self) -> MutableMapping[str, Any]:
        return {
            "meta": {
                "type": self.__meta__.type,
            },
            **self.dict(),
        }

    def get_context(self) -> MutableMapping[str, Any]:
        return self.get_data_context()
