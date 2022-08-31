from datetime import datetime
from typing import Any, Mapping, MutableMapping, Set, Type, cast

from pydantic import BaseModel, Field
from pydantic.fields import ModelField
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

    @property
    def types(self) -> Set[SnippetType]:
        return set(self._types.values())


def list_snippet_types() -> Set[SnippetType]:
    return SnippetTypeList().types


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

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            if key in ("id", "events", "created_at"):
                continue
            ret[key] = cls.get_widget(val)
        return ret

    @classmethod
    def get_widget(cls, field: ModelField) -> Mapping[str, Any]:

        if "widget" in field.field_info.extra:
            widget = {"ui:widget": field.field_info.extra["widget"]}
            if field.field_info.extra["widget"] != "hidden":
                widget["ui:placeholder"] = field.field_info.extra.get(
                    "placeholder", field.name
                )
            return widget

        if field.is_complex():

            if isinstance(field.get_default(), list):
                items = {}
                for key, val in field.type_.__fields__.items():
                    items[key] = cls.get_widget(val)
                ret: Mapping[str, Any] = {"items": items}
                return ret

        return {
            "ui:widget": {bool: "select"}.get(field.type_, "text"),
            "ui:placeholder": field.field_info.extra.get("placeholder", field.name),
        }
