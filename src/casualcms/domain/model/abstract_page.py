import enum
import re
from collections import defaultdict
from typing import Any, Iterable, Optional, Set, Type, TypeVar, cast

from pydantic import BaseModel, Field
from pydantic._internal._model_construction import ModelMetaclass
from result import Err, Ok, Result

from casualcms.domain.exceptions import MissingMetaError
from casualcms.domain.model.abstract import BaseUIModel
from casualcms.domain.model.fields import SlugField

from .breadcrumb import Breadcrumb, BreadcrumbItem
from .site import Site


class AbstractPageError(Exception):
    ...


class PageTypeError(enum.Enum):
    unregistered = "Unregistered type"


PageType = Type["AbstractPage"]
LazyPageType = str | PageType


class PublicMetadata(BaseModel):
    """Metadata exposed to the API"""

    breadcrumb: Breadcrumb
    type: str
    path: str
    canonical_url: str


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


class PageMeta:
    template: str
    parent_types: Optional[Iterable[PageType]]
    abstract: bool
    type: str
    title: str

    def __init__(
        self,
        template: str,
        parent_types: Optional[Iterable[PageType]],
        abstract: bool,
        type: str,
        title: str,
    ) -> None:
        self.template = template
        self.parent_types = parent_types
        self.abstract = abstract
        self.type = type
        self.title = title


class PageMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):  # type: ignore
        new_namespace = {**namespace}
        short_name = f"{namespace['__qualname__']}"
        long_name = f"{namespace['__module__']}:{short_name}"
        page_meta = None
        if "Meta" in namespace:
            meta = cast(object, namespace.pop("Meta"))
            type_ = getattr(meta, "type", long_name)
            page_meta = PageMeta(
                template=getattr(meta, "template", ""),
                abstract=getattr(meta, "abstract", False),
                parent_types=getattr(meta, "parent_types", []),
                type=type_,
                title=getattr(
                    meta,
                    "title",
                    re.sub("([A-Z])", r" \g<0>", short_name).strip(),
                ),
            )
            new_namespace["__meta__"] = page_meta
        else:
            raise MissingMetaError(long_name)
        ret = super().__new__(  # type: ignore
            mcls, name, bases, new_namespace, **kwargs  # type: ignore
        )
        # inject jsonschema title in pydantic config here
        ret.model_config["title"] = page_meta.title  # type: ignore
        if not page_meta.abstract:
            TypeTree().register(
                # ret is a metaclass for pylance
                ret,  # type: ignore
                page_meta.parent_types or None,
            )
        return ret  # type: ignore


class AbstractPage(BaseUIModel, metaclass=PageMetaclass):
    __meta__: PageMeta

    slug: SlugField = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    site: Optional["Site"] = Field(None, exclude=True)
    parent: Optional["AbstractPage"] = Field(None, exclude=True)

    class Meta:
        ...

    def __init__(self, **kwargs: Any) -> None:  # type: ignore
        if self.__meta__.abstract is True:
            raise AbstractPageError(f"Page {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    @property
    def metadata(self) -> PublicMetadata:
        items: list[BreadcrumbItem] = []
        p: AbstractPage = self

        while True:
            item = BreadcrumbItem(
                item="",
                name=p.title,
                position=0,
                slug=p.slug,
            )
            items.append(item)
            if p.parent is None:
                if self.site:
                    item.url = self.site.url + "/"
                    # Published page root page has no slug
                    item.path = ""
                else:
                    # Draft page case
                    item.url = ""
                    item.path = f"/{p.slug}"
                break
            p = p.parent

        last_item = None
        ordered_items: list[BreadcrumbItem] = []

        for pos, item in enumerate(reversed(items), start=1):
            item.position = pos
            if last_item is not None and pos == 2:
                item.url = last_item.url + item.slug
                item.path = last_item.path + f"/{item.slug}"
            elif last_item is not None:
                item.url = last_item.url + f"/{item.slug}"
                item.path = last_item.path + f"/{item.slug}"
            last_item = item
            ordered_items.append(item)

        return PublicMetadata(
            type=self.__meta__.type,
            path=ordered_items[-1].path,
            canonical_url=ordered_items[-1].url,
            breadcrumb=Breadcrumb(itemListElement=ordered_items),
        )


Page_contra = TypeVar("Page_contra", bound=AbstractPage, contravariant=True)
