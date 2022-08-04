"""Account repository."""
import abc
import enum
from typing import Optional, Sequence

from ..model import Page
from .base import AbstractRepository, RepositoryResult


class PageRepositoryError(enum.Enum):
    page_not_found = "Page not found"
    page_broken_treepath = "Page not found"  # we can set the same error message


PageRepositoryResult = RepositoryResult[Page, PageRepositoryError]
PageSequenceRepositoryResult = RepositoryResult[Sequence[Page], PageRepositoryError]


class AbstractPageRepository(AbstractRepository):
    seen: set[Page]

    @abc.abstractmethod
    async def by_id(self, id: str) -> PageRepositoryResult:
        """Fetch one page by its unique id."""

    @abc.abstractmethod
    async def by_path(self, path: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""

    @abc.abstractmethod
    async def by_parent(self, path: Optional[str]) -> PageSequenceRepositoryResult:
        """Fetch child pages of a page identified by its path."""

    @abc.abstractmethod
    async def add(self, model: Page) -> None:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def update(self, model: Page) -> None:
        """Append a new model to the repository."""
