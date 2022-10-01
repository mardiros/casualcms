"""Account repository."""
import abc
import enum
from typing import Any
from casualcms.domain.model.abstract_page import Page_contra

from casualcms.domain.model.published_page import Page

from .base import AbstractRepository, OperationResult, RepositoryResult


class PageRepositoryError(enum.Enum):
    page_model_not_found = "Page model not found"
    page_not_found = "Page not found"
    site_not_found = "Site not found"
    draft_not_found = "Draft Page not found"
    publication_error = "Cannot publish page"


PageRepositoryResult = RepositoryResult[Page[Page_contra], PageRepositoryError]
PageOperationResult = OperationResult[PageRepositoryError]


class AbstractPageRepository(AbstractRepository):
    seen: set[Page[Any]]

    @abc.abstractmethod
    async def by_draft_page_and_site(
        self, draft_id: str, site_id: str
    ) -> PageRepositoryResult[Page_contra]:
        """Fetch one page by its unique id."""

    @abc.abstractmethod
    async def by_url(self, url: str) -> PageRepositoryResult[Page_contra]:
        """Fetch one page by its url."""

    @abc.abstractmethod
    async def add(self, model: Page[Page_contra]) -> PageOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def update(self, model: Page[Page_contra]) -> PageOperationResult:
        """Update a model to the repository."""
