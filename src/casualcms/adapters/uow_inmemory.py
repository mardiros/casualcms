from result import Err, Ok

from casualcms.domain.model import Account
from casualcms.domain.model.page import Page
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractPageRepository,
)
from casualcms.domain.repositories.page import PageRepositoryError, PageRepositoryResult
from casualcms.domain.repositories.user import (
    AccountRepositoryError,
    AccountRepositoryResult,
)
from casualcms.service.unit_of_work import AbstractUnitOfWork


class AccountInMemoryRepository(AbstractAccountRepository):
    accounts: dict[str, Account] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""
        if username in self.accounts:
            return Ok(self.accounts[username])
        return Err(AccountRepositoryError.user_not_found)

    async def add(self, model: Account) -> None:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.accounts[model.username] = model


class PageInMemoryRepository(AbstractPageRepository):
    pages: dict[str, Page] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def by_path(self, path: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        if path in self.pages:
            return Ok(self.pages[path])
        return Err(PageRepositoryError.page_not_found)

    async def add(self, model: Page) -> None:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.pages[model.path] = model


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.accounts = AccountInMemoryRepository()
        self.pages = PageInMemoryRepository()
        self.committed: bool | None = None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
