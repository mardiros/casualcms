"""Account repository."""
import abc
import enum

from ..model import Account
from .base import AbstractRepository, OperationResult, RepositoryResult


class AccountRepositoryError(enum.Enum):
    user_not_found = "Unknown user"
    integrity_error = "Duplicate user account"


AccountRepositoryResult = RepositoryResult[Account, AccountRepositoryError]
AccountOperationResult = OperationResult[AccountRepositoryError]


class AbstractAccountRepository(AbstractRepository):
    seen: set[Account]

    @abc.abstractmethod
    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""

    @abc.abstractmethod
    async def add(self, model: Account) -> AccountOperationResult:
        """Append a new model to the repository."""
