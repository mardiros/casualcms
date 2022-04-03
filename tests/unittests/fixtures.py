import abc

from result import Err, Ok

from casualcms.api.domain.model import Account
from casualcms.api.domain.repositories import AbstractAccountRepository
from casualcms.api.domain.repositories.user import (
    AccountRepositoryError,
    AccountRepositoryResult,
)
from casualcms.api.service.unit_of_work import AbstractUnitOfWork


class AccountInMemoryRepository(AbstractAccountRepository):
    accounts: dict[str, Account] = {}

    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""
        if username in self.accounts:
            return Ok(self.accounts[username])
        return Err(AccountRepositoryError.user_not_found)

    async def add(self, model: Account) -> None:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.accounts[model.username] = model


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.accounts = AccountInMemoryRepository()
        self.committed = None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
