"""Account repository."""
import abc
import enum
from typing import Any

from casualcms.domain.model import PublishedPage

from .base import AbstractRepository, OperationResult, RepositoryResult


class PageRepositoryError(enum.Enum):
    page_model_not_found = "Page model not found"
    page_not_found = "Page not found"
    site_not_found = "Site not found"
    draft_not_found = "Draft Page not found"
    publication_error = "Cannot publish page"


PageRepositoryResult = RepositoryResult[PublishedPage[Any], PageRepositoryError]
PageOperationResult = OperationResult[PageRepositoryError]


class AbstractPageRepository(AbstractRepository):
    seen: set[PublishedPage[Any]]

    @abc.abstractmethod
    async def by_draft_page_and_site(
        self, draft_id: str, site_id: str
    ) -> PageRepositoryResult:
        """Fetch one page by its unique id."""

    @abc.abstractmethod
    async def by_url(self, url: str) -> PageRepositoryResult:
        """Fetch one page by its url."""

    @abc.abstractmethod
    async def add(self, model: PublishedPage[Any]) -> PageOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def update(self, model: PublishedPage[Any]) -> PageOperationResult:
        """Update a model to the repository."""
