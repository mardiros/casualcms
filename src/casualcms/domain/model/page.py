from collections import defaultdict
from datetime import datetime
from typing import Any, Iterable, MutableMapping, Optional, Set, Type, cast

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from casualcms.domain.messages import Event


class AbstractPageError(Exception):
    ...


PageType = Type["Page"]
LazyPageType = str | PageType


class TypeTree:
    _roots: Set[PageType] = set()
    _childs: dict[str, Set[PageType]] = defaultdict(set)

    def register(
        self, typ: PageType, parents: Optional[Iterable[LazyPageType]]
    ) -> None:
        if parents:
            for parent in parents:
                parent_typ = parent if isinstance(parent, str) else parent.__meta__.type
                self._childs[parent_typ].add(typ)
        else:
            self._roots.add(typ)

    def roots(self) -> Set[PageType]:
        return self._roots

    def get_childs(self, parent: LazyPageType) -> Set[PageType]:
        parent_typ = parent if isinstance(parent, str) else parent.__meta__.type
        return self._childs.get(parent_typ) or set()


def get_available_subtypes(parent: PageType | str | None) -> Set[PageType]:
    """Get the parent page for given type."""
    if parent is None:
        return TypeTree().roots()
    return TypeTree().get_childs(parent)


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
                type=f"{namespace['__module__']}:{name}",
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
