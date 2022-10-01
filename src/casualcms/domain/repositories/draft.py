"""Account repository."""
import abc
import enum
from typing import Any, Optional, Sequence

from casualcms.domain.model import Page_contra

from ..model import DraftPage
from .base import AbstractRepository, OperationResult, RepositoryResult


class DraftRepositoryError(enum.Enum):
    page_not_found = "Page not found"
    page_broken_treepath = "Page not found"  # we can set the same error message
    page_has_children = "Page has child pages"
    site_not_found = "Site not found"
    publication_error = "Cannot publish page"


DraftRepositoryResult = RepositoryResult[DraftPage[Page_contra], DraftRepositoryError]
DraftSequenceRepositoryResult = RepositoryResult[
    Sequence[DraftPage[Page_contra]], DraftRepositoryError
]
DraftOperationResult = OperationResult[DraftRepositoryError]


class AbstractDraftRepository(AbstractRepository):
    seen: set[DraftPage[Any]]

    @abc.abstractmethod
    async def by_id(self, id: str) -> DraftRepositoryResult[Page_contra]:
        """Fetch one page by its unique id."""

    @abc.abstractmethod
    async def by_path(self, path: str) -> DraftRepositoryResult[Page_contra]:
        """Fetch one page by its unique path."""

    @abc.abstractmethod
    async def by_parent(
        self, path: Optional[str]
    ) -> DraftSequenceRepositoryResult[Page_contra]:
        """Fetch child pages of a page identified by its path."""

    @abc.abstractmethod
    async def add(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def update(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Remove the model from the repository."""
