import enum
import re
from collections import defaultdict
from typing import (
    Any,
    Iterable,
    Mapping,
    MutableSequence,
    Optional,
    Set,
    Type,
    TypeVar,
    cast,
)

from pydantic import BaseModel, ConstrainedStr, Field
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass
from result import Err, Ok, Result


class Slug(ConstrainedStr):
    regex = re.compile("^[^/]+$")
    strip_whitespace = True


class AbstractPageError(Exception):
    ...


class PageTypeError(enum.Enum):
    unregistered = "Unregistered type"


PageType = Type["AbstractPage"]
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

    def resolve_type(self, typ: str) -> Result[PageType, PageTypeError]:
        try:
            return Ok(self._types[typ])
        except KeyError:
            return Err(PageTypeError.unregistered)

    def get_childs(self, parent: LazyPageType) -> Set[PageType]:
        parent_typ = parent if isinstance(parent, str) else parent.__meta__.type
        return self._childs.get(parent_typ) or set()


def get_available_subtypes(parent: PageType | str | None) -> Set[PageType]:
    """Get the parent page for given type."""
    if parent is None:
        return TypeTree().roots()
    return TypeTree().get_childs(parent)


def resolve_page_type(typ: str) -> Result[PageType, PageTypeError]:
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

    slug: Slug = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    parent: Optional["AbstractPage"] = Field(None, exclude=True)

    class Meta:
        ...

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractPageError(f"Page {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    @property
    def path(self) -> str:
        slugs = []
        page: Optional["AbstractPage"] = self
        while page:
            slugs.append(page.slug)
            page = page.parent
        return "/" + "/".join(reversed(slugs))

    @property
    def metadata(self) -> Mapping[str, Any]:
        breadcrumb: MutableSequence[Mapping[str, str]] = []
        p: Optional[AbstractPage] = self
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
            "type": self.__meta__.type,
            "path": self.path,
            "breadcrumb": breadcrumb,
        }

    @classmethod
    def ui_schema(cls) -> Mapping[str, Any]:
        ret: dict[str, Any] = {}
        for key, val in cls.__fields__.items():
            if key in ("parent",):
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
            "ui:widget": {bool: "checkbox"}.get(field.type_, "text"),
            "ui:placeholder": field.field_info.extra.get("placeholder", field.name),
        }


PageImpl = TypeVar("PageImpl", bound=AbstractPage)
