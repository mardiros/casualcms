"""Account repository."""
import abc
import enum
from types import EllipsisType
from typing import Sequence

from casualcms.domain.model import Site

from .base import AbstractRepository, RepositoryResult


class SiteRepositoryError(enum.Enum):
    site_not_found = "Site not found"


SiteRepositoryResult = RepositoryResult[Site, SiteRepositoryError]
SiteSequenceRepositoryResult = RepositoryResult[Sequence[Site], SiteRepositoryError]
SiteOperationResult = RepositoryResult[EllipsisType, SiteRepositoryError]


class AbstractSiteRepository(AbstractRepository):
    seen: set[Site]

    @abc.abstractmethod
    async def add(self, model: Site) -> None:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def list(self) -> SiteSequenceRepositoryResult:
        """Fetch all sites."""

    @abc.abstractmethod
    async def by_id(self, id: str) -> SiteRepositoryResult:
        """Fetch the site with given id."""

    @abc.abstractmethod
    async def by_hostname(self, hostname: str) -> SiteRepositoryResult:
        """Fetch the site with given hostname."""

    @abc.abstractmethod
    async def remove(self, model: Site) -> SiteOperationResult:
        """Remove given model from the repository."""
