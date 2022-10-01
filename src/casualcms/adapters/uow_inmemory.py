from typing import Any, Iterable, Optional
from urllib.parse import urlparse

from result import Err, Ok

from casualcms.config import Settings
from casualcms.domain.model import (
    Account,
    AuthnToken,
    DraftPage,
    Page_contra,
    PublishedPage,
    Setting,
    Site,
    Snippet,
    Snippet_contra,
)
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractDraftRepository,
)
from casualcms.domain.repositories.authntoken import (
    AuthnTokenOperationResult,
    AuthnTokenRepositoryError,
    AuthnTokenRepositoryResult,
)
from casualcms.domain.repositories.draft import (
    DraftOperationResult,
    DraftRepositoryError,
    DraftRepositoryResult,
    DraftSequenceRepositoryResult,
)
from casualcms.domain.repositories.page import (
    AbstractPageRepository,
    PageOperationResult,
    PageRepositoryError,
    PageRepositoryResult,
)
from casualcms.domain.repositories.setting import (
    AbstractSettingRepository,
    SettingOperationResult,
    SettingRepositoryError,
    SettingRepositoryResult,
    SettingSequenceRepositoryResult,
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
    AccountOperationResult,
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

    async def add(self, model: Account) -> AccountOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.accounts[model.username] = model  # type: ignore
        return Ok(...)


class DraftInMemoryRepository(AbstractDraftRepository):
    pages: dict[str, DraftPage[Any]] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def by_id(self, id: str) -> DraftRepositoryResult[Page_contra]:
        """Fetch one page by its unique path."""
        for page in self.pages.values():
            if page.id == id:
                return Ok(page)

        return Err(DraftRepositoryError.page_not_found)

    async def by_path(self, path: str) -> DraftRepositoryResult[Page_contra]:
        """Fetch one page by its unique path."""
        if path in self.pages:
            return Ok(self.pages[path])
        return Err(DraftRepositoryError.page_not_found)

    async def by_parent(
        self, path: Optional[str]
    ) -> DraftSequenceRepositoryResult[Page_contra]:
        """Fetch one page by its unique path."""
        ret: list[DraftPage[Page_contra]] = []
        if path:
            cnt = len(path.strip("/").split("/")) + 1
        else:
            cnt = 1
        for key, page in self.pages.items():
            if key.startswith(path or "") and len(key.strip("/").split("/")) == cnt:
                ret.append(page)

        return Ok(ret)

    async def add(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.pages[model.path] = model
        return Ok(...)

    async def remove(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Remove the model from the repository."""
        self.seen.add(model)
        del self.pages[model.path]
        return Ok(...)

    async def update(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        k = None
        for key, page in self.pages.items():
            if page.id == model.id:
                k = key
                break
        else:
            Err(DraftRepositoryError.page_not_found)
        if k:
            del self.pages[k]
        self.pages[model.path] = model
        return Ok(...)


class PageInMemoryRepository(AbstractPageRepository):
    pages: dict[tuple[str, str], PublishedPage[Any]] = {}

    async def by_draft_page_and_site(
        self, draft_id: str, site_id: str
    ) -> PageRepositoryResult[Page_contra]:
        """Fetch one page by its unique id."""
        try:
            ppage = self.pages[draft_id, site_id]
        except KeyError:
            return Err(PageRepositoryError.page_not_found)
        return Ok(ppage)

    async def by_url(self, url: str) -> PageRepositoryResult[Page_contra]:
        url_ = urlparse(url)
        hostname, path = url_.netloc, url_.path
        path = f"//{hostname}{path.rstrip('/')}"
        page = [p for p in self.pages.values() if p.path == path]

        if not page:
            return Err(PageRepositoryError.page_not_found)
        return Ok(page[0])

    async def add(self, model: PublishedPage[Page_contra]) -> PageOperationResult:
        """Append a new model to the repository."""
        self.pages[model.draft_id, model.site.id] = model
        return Ok(...)

    async def update(self, model: PublishedPage[Page_contra]) -> PageOperationResult:
        """Update a model to the repository."""
        self.pages[model.draft_id, model.site.id] = model
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
        rpage: DraftRepositoryResult[Any] = await DraftInMemoryRepository().by_path(
            model.root_page_path
        )
        if rpage.is_err():
            return Err(SiteRepositoryError.root_page_not_found)
        model.draft_id = rpage.unwrap().id
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
    snippets: dict[str, Snippet[Any]] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def list(
        self, type: Optional[str] = None
    ) -> SnippetSequenceRepositoryResult[Snippet_contra]:
        """List all snippets, optionally filters on their types."""
        values: Iterable[Snippet[Snippet_contra]] = self.snippets.values()
        if type:
            values = filter(lambda s: s.type == type, values)
        return Ok(sorted(values, key=lambda s: s.key))

    async def by_id(self, id: str) -> SnippetRepositoryResult[Snippet_contra]:
        """Fetch one snippet by its unique id."""
        for snippet in self.snippets.values():
            if snippet.id == id:
                return Ok(snippet)
        return Err(SnippetRepositoryError.snippet_not_found)

    async def by_key(self, key: str) -> SnippetRepositoryResult[Snippet_contra]:
        """Fetch one snippet by its unique key."""
        try:
            return Ok(self.snippets[key])
        except KeyError:
            return Err(SnippetRepositoryError.snippet_not_found)

    async def add(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.snippets[model.key] = model
        return Ok(...)

    async def remove(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Remove the model from the repository."""
        self.seen.add(model)
        del self.snippets[model.key]
        return Ok(...)

    async def update(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        k = None
        for key, snippet in self.snippets.items():
            if snippet.id == model.id:
                k = key
                break
        if k:
            del self.snippets[k]
        self.snippets[model.key] = model
        return Ok(...)


class SettingInMemoryRepository(AbstractSettingRepository):
    settings: dict[tuple[str, str], Setting] = {}

    def __init__(self) -> None:
        self.seen = set()

    async def list(
        self, hostname: Optional[str] = None
    ) -> SettingSequenceRepositoryResult:
        """List all settings, optionally filters on their types."""
        values: Iterable[Setting] = self.settings.values()
        if hostname:
            values = filter(lambda s: s.hostname == hostname, values)
        return Ok(sorted(values, key=lambda s: (s.hostname, s.__meta__.key)))

    async def by_id(self, id: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique id."""
        for setting in self.settings.values():
            if setting.id == id:
                return Ok(setting)
        return Err(SettingRepositoryError.setting_not_found)

    async def by_key(self, hostname: str, key: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique slug."""
        try:
            return Ok(self.settings[(hostname, key)])
        except KeyError:
            return Err(SettingRepositoryError.setting_not_found)

    async def add(self, model: Setting) -> SettingOperationResult:
        """Append a new model to the repository."""
        self.seen.add(model)
        self.settings[(model.hostname, model.__meta__.key)] = model
        return Ok(...)

    async def remove(self, model: Setting) -> SettingOperationResult:
        """Remove the model from the repository."""
        self.seen.add(model)
        del self.settings[(model.hostname, model.__meta__.key)]
        return Ok(...)

    async def update(self, model: Setting) -> SettingOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        k = None
        for key, setting in self.settings.items():
            if setting.id == model.id:
                k = key
                break
        if k:
            del self.settings[k]
        self.settings[(model.hostname, model.__meta__.key)] = model
        return Ok(...)


class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self, settings: Settings) -> None:
        self.accounts = AccountInMemoryRepository()
        self.authn_tokens = AuthnTokenInMemoryRepository()
        self.drafts = DraftInMemoryRepository()
        self.pages = PageInMemoryRepository()
        self.snippets = SnippetInMemoryRepository()
        self.sites = SiteInMemoryRepository()
        self.settings = SettingInMemoryRepository()
        self.committed: bool | None = None
        self.initialized = False

    async def initialize(self) -> None:
        self.initialized = True

    async def dispose(self) -> None:
        self.accounts.accounts.clear()  # type: ignore
        self.drafts.pages.clear()  # type: ignore
        self.pages.pages.clear()  # type: ignore
        self.sites.sites.clear()  # type: ignore
        self.snippets.snippets.clear()  # type: ignore
        self.authn_tokens.tokens.clear()  # type: ignore

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
