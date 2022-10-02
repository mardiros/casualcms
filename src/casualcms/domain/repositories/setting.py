"""Account repository."""
import abc
import enum
from typing import Any, Optional, Sequence

from casualcms.domain.model.abstract_setting import Setting_contra

from ..model import Setting
from .base import AbstractRepository, OperationResult, RepositoryResult


class SettingRepositoryError(enum.Enum):
    setting_not_found = "Setting not found"
    site_not_found = "Site not found"


SettingRepositoryResult = RepositoryResult[
    Setting[Setting_contra], SettingRepositoryError
]
SettingSequenceRepositoryResult = RepositoryResult[
    Sequence[Setting[Setting_contra]], SettingRepositoryError
]
SettingOperationResult = OperationResult[SettingRepositoryError]


class AbstractSettingRepository(AbstractRepository):
    seen: set[Setting[Any]]

    @abc.abstractmethod
    async def list(
        self, hostname: Optional[str] = None
    ) -> SettingSequenceRepositoryResult[Setting_contra]:
        """List all settings, optionally filters on their types."""

    @abc.abstractmethod
    async def by_id(self, id: str) -> SettingRepositoryResult[Setting_contra]:
        """Fetch one setting by its unique id."""

    @abc.abstractmethod
    async def by_key(
        self, hostname: str, key: str
    ) -> SettingRepositoryResult[Setting_contra]:
        """Fetch one setting by its unique key for a given hostname."""

    @abc.abstractmethod
    async def add(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Remove the model from the repository."""

    @abc.abstractmethod
    async def update(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Update a model from the repository."""
