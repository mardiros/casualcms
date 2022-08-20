from typing import Iterable, Optional

from result import Err, Ok

from casualcms.config import Settings
from casualcms.domain.model import Account, AuthnToken, Page, Site
from casualcms.domain.model.snippet import Snippet
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractPageRepository,
)
from casualcms.domain.repositories.authntoken import (
    AuthnTokenOperationResult,
    AuthnTokenRepositoryError,
    AuthnTokenRepositoryResult,
)
from casualcms.domain.repositories.page import (
    PageOperationResult,
    PageRepositoryError,
    PageRepositoryResult,
    PageSequenceRepositoryResult,
)
from casualcms.domain.repositories.site import (
    AbstractSiteRepository,
    SiteOperationResult,
    SiteRepositoryError,
    SiteRepositoryResult,
    SiteSequenceRepositoryResult,
)
from casualcms.domain.repositories.snippet import (
    AbstractSnippetRepository,
    SnippetOperationResult,
    SnippetRepositoryError,
    SnippetRepositoryResult,
    SnippetSequenceRepositoryResult,
)
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
        self.accounts[model.username] = model  # type: ignore


class PageInMemoryRepository(AbstractPageRepository):
    pages: dict[str, Page] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def by_id(self, id: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        for page in self.pages.values():
            if page.id == id:
                return Ok(page)

        return Err(PageRepositoryError.page_not_found)

    async def by_path(self, path: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        if path in self.pages:
            return Ok(self.pages[path])
        return Err(PageRepositoryError.page_not_found)

    async def by_parent(self, path: Optional[str]) -> PageSequenceRepositoryResult:
        """Fetch one page by its unique path."""
        ret: list[Page] = []
        if path:
            cnt = len(path.strip("/").split("/")) + 1
        else:
            cnt = 1
        for key, page in self.pages.items():
            if key.startswith(path or "") and len(key.strip("/").split("/")) == cnt:
                ret.append(page)

        return Ok(ret)

    async def add(self, model: Page) -> PageOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.pages[model.path] = model
        return Ok(...)

    async def remove(self, model: Page) -> PageOperationResult:
        """Remove the model from the repository."""
        self.seen.add(model)
        del self.pages[model.path]
        return Ok(...)

    async def update(self, model: Page) -> PageOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        k = None
        for key, page in self.pages.items():
            if page.id == model.id:
                k = key
                break
        else:
            Err(PageRepositoryError.page_not_found)
        if k:
            del self.pages[k]
        self.pages[model.path] = model
        return Ok(...)


class AuthnTokenInMemoryRepository(AbstractAuthnRepository):
    tokens: dict[str, AuthnToken] = {}

    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch one user account by its unique username."""
        if token in self.tokens:
            return Ok(self.tokens[token])
        return Err(AuthnTokenRepositoryError.token_not_found)

    async def add(self, model: AuthnToken) -> AuthnTokenOperationResult:
        """Append a new model to the repository."""
        if model.token in self.tokens:
            return Err(AuthnTokenRepositoryError.integrity_error)
        self.tokens[model.token] = model  # type: ignore
        return Ok(...)

    async def remove(self, token: str) -> AuthnTokenOperationResult:
        """Delete a new model to the repository."""
        if token not in self.tokens:
            return Err(AuthnTokenRepositoryError.token_not_found)
        del self.tokens[token]
        return Ok(...)


class SiteInMemoryRepository(AbstractSiteRepository):
    sites: list[Site] = []

    def __init__(self) -> None:
        self.seen = set()

    async def add(self, model: Site) -> SiteOperationResult:
        """Append a new model to the repository."""
        self.sites.append(model)
        self.sites.sort(key=lambda s: s.hostname)
        self.seen.add(model)
        return Ok(...)

    async def list(self) -> SiteSequenceRepositoryResult:
        """Fetch all sites."""
        return Ok(self.sites)

    async def by_id(self, id: str) -> SiteRepositoryResult:
        """Fetch site by id."""
        for site in self.sites:
            if site.id == id:
                return Ok(site)
        return Err(SiteRepositoryError.site_not_found)

    async def by_hostname(self, hostname: str) -> SiteRepositoryResult:
        """Fetch all sites."""
        for site in self.sites:
            if site.hostname == hostname:
                return Ok(site)
        return Err(SiteRepositoryError.site_not_found)

    async def update(self, model: Site) -> SiteOperationResult:
        """Update given model into the repository."""
        sites: list[Site] = []
        for site in self.sites:
            if site.id != model.id:
                sites.append(site)
        sites.append(model)
        self.sites = sites
        return Ok(...)

    async def remove(self, model: Site) -> SiteOperationResult:
        """Remove given model from the repository."""
        sites: list[Site] = []
        for site in self.sites:
            if site.id != model.id:
                sites.append(site)
        self.sites = sites
        return Ok(...)


class SnippetInMemoryRepository(AbstractSnippetRepository):
    snippets: dict[str, Snippet] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def list(self, type: Optional[str] = None) -> SnippetSequenceRepositoryResult:
        """List all snippets, optionally filters on their types."""
        values: Iterable[Snippet] = self.snippets.values()
        if type:
            values = filter(lambda s: s.__meta__.type == type, values)
        return Ok(sorted(values, key=lambda s: s.slug))

    async def by_id(self, id: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique id."""
        for snippet in self.snippets.values():
            if snippet.id == id:
                return Ok(snippet)
        return Err(SnippetRepositoryError.snippet_not_found)

    async def by_slug(self, slug: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique slug."""
        try:
            return Ok(self.snippets[slug])
        except KeyError:
            return Err(SnippetRepositoryError.snippet_not_found)

    async def add(self, model: Snippet) -> SnippetOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.snippets[model.slug] = model
        return Ok(...)

    async def remove(self, model: Snippet) -> SnippetOperationResult:
        """Remove the model from the repository."""
        self.seen.add(model)
        del self.snippets[model.slug]
        return Ok(...)

    async def update(self, model: Snippet) -> SnippetOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        k = None
        for key, snippet in self.snippets.items():
            if snippet.id == model.id:
                k = key
                break
        if k:
            del self.snippets[k]
        self.snippets[model.slug] = model
        return Ok(...)


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self, settings: Settings) -> None:
        self.accounts = AccountInMemoryRepository()
        self.pages = PageInMemoryRepository()
        self.snippets = SnippetInMemoryRepository()
        self.sites = SiteInMemoryRepository()
        self.authn_tokens = AuthnTokenInMemoryRepository()
        self.committed: bool | None = None
        self.initialized = False

    async def initialize(self) -> None:
        self.initialized = True

    async def dispose(self) -> None:
        self.accounts.accounts.clear()  # type: ignore
        self.pages.pages.clear()  # type: ignore
        self.sites.sites.clear()  # type: ignore

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
