"""Account repository."""
import abc
import enum

from casualcms.domain.model.page import Page

from .base import AbstractRepository, OperationResult, RepositoryResult


class PageRepositoryError(enum.Enum):
    page_not_found = "Page not found"
    site_not_found = "Site not found"
    draft_not_found = "Draft Page not found"
    publication_error = "Cannot publish page"


PageRepositoryResult = RepositoryResult[Page, PageRepositoryError]
PageOperationResult = OperationResult[PageRepositoryError]


class AbstractPageRepository(AbstractRepository):
    seen: set[Page]

    @abc.abstractmethod
    async def by_page_and_site(
        self, page_id: str, site_id: str
    ) -> PageRepositoryResult:
        """Fetch one page by its unique id."""

    @abc.abstractmethod
    async def add(self, model: Page) -> PageOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def update(self, model: Page) -> PageOperationResult:
        """Update a model to the repository."""
