from collections import defaultdict
from datetime import datetime
from typing import (
    Any,
    Iterable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Optional,
    Set,
    Type,
    cast,
)

from pydantic import BaseModel, Field
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass

from casualcms.domain.messages import Event
from casualcms.domain.messages.commands import generate_id

uuid = str


class AbstractPageError(Exception):
    ...


class UnregisterType(Exception):
    def __init__(self, typ: str) -> None:
        super().__init__(f"Unregistered type {typ}")


PageType = Type["Page"]
LazyPageType = str | PageType


class TypeTree:
    _roots: Set[PageType] = set()
    _childs: dict[str, Set[PageType]] = defaultdict(set)
    _types: dict[str, PageType] = {}

    def register(
        self, typ: PageType, parents: Optional[Iterable[LazyPageType]]
    ) -> None:
        self._types[typ.__meta__.type] = typ
        if parents:
            for parent in parents:
                parent_typ = parent if isinstance(parent, str) else parent.__meta__.type
                self._childs[parent_typ].add(typ)
        else:
            self._roots.add(typ)

    def roots(self) -> Set[PageType]:
        return self._roots

    def resolve_type(self, typ: str) -> PageType:
        try:
            return self._types[typ]
        except KeyError:
            raise UnregisterType(typ)

    def get_childs(self, parent: LazyPageType) -> Set[PageType]:
        parent_typ = parent if isinstance(parent, str) else parent.__meta__.type
        return self._childs.get(parent_typ) or set()


def get_available_subtypes(parent: PageType | str | None) -> Set[PageType]:
    """Get the parent page for given type."""
    if parent is None:
        return TypeTree().roots()
    return TypeTree().get_childs(parent)


def resolve_page_type(typ: str) -> PageType:
    return TypeTree().resolve_type(typ)


class PageMeta(BaseModel):
    template: str = Field(...)
    parent_types: Optional[Iterable[PageType]] = Field(...)
    abstract: bool = Field(...)
    type: str = Field(...)


class PageMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        page_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            page_meta = PageMeta(
                template=getattr(
                    meta,
                    "template",
                    "",  # TODO: a default template for users
                ),
                abstract=getattr(meta, "abstract", False),
                parent_types=getattr(meta, "parent_types", []),
                type=getattr(meta, "type", f"{namespace['__module__']}:{name}"),
            )
            new_namespace["__meta__"] = page_meta
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        if page_meta and not page_meta.abstract:
            TypeTree().register(ret, page_meta.parent_types or None)  # type: ignore

        return ret


class AbstractPage(BaseModel, metaclass=PageMetaclass):
    __meta__: PageMeta

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractPageError(f"Page {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    def get_template(self) -> str:
        return self.__meta__.template


class Page(AbstractPage):

    id: uuid = Field(default_factory=generate_id, exclude=True)
    slug: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)

    parent: Optional["Page"] = Field(None, exclude=True)
    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    class Meta:
        abstract = True

    @property
    def path(self) -> str:
        slugs = []
        page: Optional["Page"] = self
        while page:
            slugs.append(page.slug)
            page = page.parent
        return "/" + "/".join(reversed(slugs))

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)

    def get_data_context(self) -> MutableMapping[str, Any]:
        breadcrumb: MutableSequence[Mapping[str, str]] = []
        p: Optional[Page] = self
        while p:
            breadcrumb.insert(
                0,
                {
                    "slug": p.slug,
                    "path": p.path,
                    "title": p.title,
                },
            )
            p = p.parent
        return {
            "meta": {
                "type": self.__meta__.type,
                "path": self.path,
                "breadcrumb": breadcrumb,
            },
            **self.dict(exclude={"events", "created_at"}),
        }

    def get_context(self) -> MutableMapping[str, Any]:
        return self.get_data_context()

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            if key in ("id", "parent", "events", "created_at"):
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
            "ui:widget": {bool: "radio"}.get(field.type_, "text"),
            "ui:placeholder": field.field_info.extra.get("placeholder", field.name),
        }
