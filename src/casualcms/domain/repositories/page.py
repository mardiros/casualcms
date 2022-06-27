"""Account repository."""
import abc
import enum
from typing import Optional, Sequence

from ..model import Page
from .base import AbstractRepository, RepositoryResult


class PageRepositoryError(enum.Enum):
    page_not_found = "Page not found"


PageRepositoryResult = RepositoryResult[Page, PageRepositoryError]
PageSequenceRepositoryResult = RepositoryResult[Sequence[Page], PageRepositoryError]


class AbstractPageRepository(AbstractRepository):
    seen: set[Page]

    @abc.abstractmethod
    async def by_path(self, path: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""

    @abc.abstractmethod
    async def by_parent(self, path: Optional[str]) -> PageSequenceRepositoryResult:
        """Fetch one page by its unique path."""

    @abc.abstractmethod
    async def add(self, model: Page) -> None:
        """Append a new model to the repository."""
