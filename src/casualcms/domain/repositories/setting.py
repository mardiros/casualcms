"""Account repository."""
import abc
import enum
from typing import Optional, Sequence

from ..model import Setting
from .base import AbstractRepository, OperationResult, RepositoryResult


class SettingRepositoryError(enum.Enum):
    setting_not_found = "Setting not found"
    site_not_found = "Site not found"


SettingRepositoryResult = RepositoryResult[Setting, SettingRepositoryError]
SettingSequenceRepositoryResult = RepositoryResult[
    Sequence[Setting], SettingRepositoryError
]
SettingOperationResult = OperationResult[SettingRepositoryError]


class AbstractSettingRepository(AbstractRepository):
    seen: set[Setting]

    @abc.abstractmethod
    async def list(
        self, hostname: Optional[str] = None
    ) -> SettingSequenceRepositoryResult:
        """List all settings, optionally filters on their types."""

    @abc.abstractmethod
    async def by_id(self, id: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique id."""

    @abc.abstractmethod
    async def by_key(self, hostname: str, key: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique key for a given hostname."""

    @abc.abstractmethod
    async def add(self, model: Setting) -> SettingOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, model: Setting) -> SettingOperationResult:
        """Remove the model from the repository."""

    @abc.abstractmethod
    async def update(self, model: Setting) -> SettingOperationResult:
        """Update a model from the repository."""
