from collections import defaultdict
from datetime import datetime
from typing import Any, Iterable, MutableMapping, Optional, Set, Type, cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.adapters.resolver import resolve
from casualcms.domain.messages import Event


class AbstractPageError(Exception):
    ...


PageType = Type["Page"]


def resolve_page(value: str | PageType) -> "Page":
    if isinstance(value, str):
        value = resolve(value)
    return cast(Page, value)


class TypeTree:
    data: dict[Optional[PageType], Set[PageType]] = defaultdict(set)

    def register(self, typ: PageType, parents: Optional[Iterable[PageType]]):
        if parents:
            for parent in parents:
                self.data[parent].add(typ)
        else:
            self.data[None].add(typ)

    def roots(self) -> Set[PageType]:
        return self.data.get(None) or set()

    def get_childs(self, parent: PageType) -> Set[PageType]:
        return self.data.get(parent) or set()


def get_available_subtypes(parent: PageType | None) -> Set[PageType]:
    """Get the parent page for given type."""
    if parent is None:
        return TypeTree().roots()
    return TypeTree().get_childs(parent)


class PageMeta(BaseModel):
    template: str = Field(...)
    parent_types: Optional[Iterable[PageType]] = Field(...)
    abstract: bool = Field(...)
    type:str = Field(...)


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
                type=f"{namespace['__module__']}:{name}",
            )
            new_namespace["__meta__"] = page_meta
        ret = super().__new__(mcls, name, bases, new_namespace, **kwargs)
        if page_meta and not page_meta.abstract:
            TypeTree().register(ret, page_meta.parent_types or None)  # type: ignore

        return ret


class AbstractPage(BaseModel, metaclass=PageMetaclass):
    __meta__: PageMeta

    def __init__(self, **kwargs: Any):
        if self.__meta__.abstract is True:
            raise AbstractPageError(f"Page {self.__class__.__name__} is abstract")
        super().__init__(**kwargs)

    def get_context(self) -> MutableMapping[str, Any]:
        return self.dict(exclude={"events", "created_at"})

    def get_template(self) -> str:
        return self.__meta__.template


class Page(AbstractPage):

    id: str = Field(...)
    slug: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)

    parent: Optional["Page"] = Field(default_factory=list, exclude=True)
    events: list[Event] = Field(default_factory=list, exclude=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, exclude=True)

    @property
    def path(self) -> str:
        slugs = []
        page: Optional["Page"] = self
        while page:
            slugs.append(page.slug)
            page = page.parent
        return "/".join(reversed(slugs)) or "/"

    def __hash__(self) -> int:  # type: ignore
        return hash(self.id)
