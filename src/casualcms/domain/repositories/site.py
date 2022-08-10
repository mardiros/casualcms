"""Account repository."""
import abc
import enum
from typing import Sequence

from casualcms.domain.model import Site

from .base import AbstractRepository, RepositoryResult


class SiteRepositoryError(enum.Enum):
    site_not_found = "Site not found"


SiteRepositoryResult = RepositoryResult[Site, SiteRepositoryError]
SiteSequenceRepositoryResult = RepositoryResult[Sequence[Site], SiteRepositoryError]


class AbstractSiteRepository(AbstractRepository):
    seen: set[Site]

    @abc.abstractmethod
    async def add(self, model: Site) -> None:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def list(self) -> SiteSequenceRepositoryResult:
        """Fetch all sites."""
