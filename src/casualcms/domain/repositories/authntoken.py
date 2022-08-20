import abc
import enum

from ..model import AuthnToken
from .base import AbstractRepository, OperationResult, RepositoryResult


class AuthnTokenRepositoryError(enum.Enum):
    token_not_found = "Unknown token"
    integrity_error = "Duplicate token"


AuthnTokenRepositoryResult = RepositoryResult[AuthnToken, AuthnTokenRepositoryError]
AuthnTokenOperationResult = OperationResult[AuthnTokenRepositoryError]


class AbstractAuthnRepository(AbstractRepository):
    @abc.abstractmethod
    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch one user account by its unique username."""

    @abc.abstractmethod
    async def add(self, model: AuthnToken) -> AuthnTokenOperationResult:
        """Append a new model to the repository."""

    @abc.abstractmethod
    async def remove(self, token: str) -> AuthnTokenOperationResult:
        """Delete a new model to the repository."""
