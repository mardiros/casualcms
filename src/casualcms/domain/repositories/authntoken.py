import abc
import enum

from ..model import AuthnToken
from .base import AbstractRepository, RepositoryResult


class AuthnTokenRepositoryError(enum.Enum):
    token_not_found = "Unknown token"


AuthnTokenRepositoryResult = RepositoryResult[AuthnToken, AuthnTokenRepositoryError]


class AbstractAuthnRepository(AbstractRepository):
    @abc.abstractmethod
    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch one user account by its unique username."""

    @abc.abstractmethod
    async def add(self, model: AuthnToken) -> None:
        """Append a new model to the repository."""
