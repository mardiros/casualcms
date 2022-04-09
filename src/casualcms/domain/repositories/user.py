"""Account repository."""
import abc
import enum

from ..model import Account
from .base import AbstractRepository, RepositoryResult


class AccountRepositoryError(enum.Enum):
    user_not_found = "Unknown user"


AccountRepositoryResult = RepositoryResult[Account, AccountRepositoryError]


class AbstractAccountRepository(AbstractRepository):
    seen: set[Account]

    @abc.abstractmethod
    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""

    @abc.abstractmethod
    async def add(self, model: Account) -> None:
        """Append a new model to the repository."""
