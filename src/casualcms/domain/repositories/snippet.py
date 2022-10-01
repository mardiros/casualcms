"""Account repository."""
import abc
import enum
from typing import Any, Optional, Sequence

from casualcms.domain.model.abstract_snippet import SnippetImpl

from ..model import Snippet
from .base import AbstractRepository, OperationResult, RepositoryResult


class SnippetRepositoryError(enum.Enum):
    snippet_not_found = "Snippet not found"
    snippet_type_not_found = "Snippet Type not found"


SnippetRepositoryResult = RepositoryResult[Snippet[SnippetImpl], SnippetRepositoryError]
SnippetSequenceRepositoryResult = RepositoryResult[
    Sequence[Snippet[SnippetImpl]], SnippetRepositoryError
]
SnippetOperationResult = OperationResult[SnippetRepositoryError]


class AbstractSnippetRepository(AbstractRepository):
    seen: set[Snippet[Any]]

    @abc.abstractmethod
    async def list(
        self, type: Optional[str] = None
    ) -> SnippetSequenceRepositoryResult[SnippetImpl]:
        """List all snippets, optionally filters on their types."""

    @abc.abstractmethod
    async def by_id(self, id: str) -> SnippetRepositoryResult[SnippetImpl]:
        """Fetch one snippet by its unique id."""

    @abc.abstractmethod
    async def by_key(self, key: str) -> SnippetRepositoryResult[SnippetImpl]:
        """Fetch one snippet by its unique slug."""

    @abc.abstractmethod
    async def add(self, model: Snippet[SnippetImpl]) -> SnippetOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, model: Snippet[SnippetImpl]) -> SnippetOperationResult:
        """Remove the model from the repository."""

    @abc.abstractmethod
    async def update(self, model: Snippet[SnippetImpl]) -> SnippetOperationResult:
        """Update a model from the repository."""
