"""Account repository."""
import abc
import enum
from typing import Optional, Sequence

from ..model import Snippet
from .base import AbstractRepository, OperationResult, RepositoryResult


class SnippetRepositoryError(enum.Enum):
    snippet_not_found = "Snippet not found"


SnippetRepositoryResult = RepositoryResult[Snippet, SnippetRepositoryError]
SnippetSequenceRepositoryResult = RepositoryResult[
    Sequence[Snippet], SnippetRepositoryError
]
SnippetOperationResult = OperationResult[SnippetRepositoryError]


class AbstractSnippetRepository(AbstractRepository):
    seen: set[Snippet]

    @abc.abstractmethod
    async def list(self, type: Optional[str] = None) -> SnippetSequenceRepositoryResult:
        """List all snippets, optionally filters on their types."""

    @abc.abstractmethod
    async def by_id(self, id: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique id."""

    @abc.abstractmethod
    async def by_key(self, key: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique slug."""

    @abc.abstractmethod
    async def add(self, model: Snippet) -> SnippetOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, model: Snippet) -> SnippetOperationResult:
        """Remove the model from the repository."""

    @abc.abstractmethod
    async def update(self, model: Snippet) -> SnippetOperationResult:
        """Update a model from the repository."""
