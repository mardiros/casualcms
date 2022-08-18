"""Account repository."""
import abc
import enum
from types import EllipsisType
from typing import Sequence

from ..model import Snippet
from .base import AbstractRepository, RepositoryResult


class SnippetRepositoryError(enum.Enum):
    snippet_not_found = "Snippet not found"
    snippet_broken_treepath = "Snippet not found"  # we can set the same error message
    snippet_has_children = "Snippet has child pages"


SnippetRepositoryResult = RepositoryResult[Snippet, SnippetRepositoryError]
SnippetSequenceRepositoryResult = RepositoryResult[
    Sequence[Snippet], SnippetRepositoryError
]
SnippetOperationResult = RepositoryResult[EllipsisType, SnippetRepositoryError]


class AbstractSnippetRepository(AbstractRepository):
    seen: set[Snippet]

    @abc.abstractmethod
    async def list(self) -> SnippetSequenceRepositoryResult:
        """list all snippets."""

    @abc.abstractmethod
    async def by_slug(self, slug: str) -> SnippetRepositoryResult:
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
