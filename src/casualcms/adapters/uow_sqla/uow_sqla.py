from operator import and_
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Type, cast
from urllib.parse import urlparse

from result import Err, Ok
from sqlalchemy import alias, delete, text  # type: ignore
from sqlalchemy.engine.cursor import CursorResult  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from casualcms.config import Settings
from casualcms.domain.model import (
    Account,
    AuthnToken,
    DraftPage,
    Page,
    Site,
    resolve_page_type,
)
from casualcms.domain.model.setting import Setting, SettingType, resolve_setting_type
from casualcms.domain.model.snippet import Snippet, SnippetType, resolve_snippet_type
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractDraftRepository,
    AbstractSiteRepository,
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

from . import orm


def format_draft_page(page: DraftPage) -> Dict[str, Any]:
    """Format the page to a dict ready to be inserted in the orm.drafts."""
    p: Dict[str, Any] = page.dict()
    formated_page: Dict[str, Any] = {
        "id": page.id,
        "type": page.__meta__.type,
        "created_at": page.created_at,
        "slug": p.pop("slug"),
        "title": p.pop("title"),
        "description": p.pop("description"),
    }
    formated_page["body"] = p
    return formated_page


def format_page(page: Page) -> Dict[str, Any]:
    formated_page: Dict[str, Any] = page.dict(exclude={"site", "draft"})
    formated_page["id"] = page.id
    formated_page["created_at"] = page.created_at
    formated_page["draft_id"] = page.draft.id
    formated_page["site_id"] = page.site.id
    return formated_page


def format_snippet(snippet: Snippet) -> Dict[str, Any]:
    formated_snippet: Dict[str, Any] = {
        "id": snippet.id,
        "type": snippet.__meta__.type,
        "created_at": snippet.created_at,
        "key": snippet.key,
        "body": snippet.dict(exclude={"key"}),
    }
    return formated_snippet


def format_setting(site_id: str, setting: Setting) -> Dict[str, Any]:
    formated_setting: Dict[str, Any] = {
        "id": setting.id,
        "key": setting.__meta__.key,
        "created_at": setting.created_at,
        "site_id": site_id,
        "value": setting.dict(exclude={"hostname", "slug"}),
    }
    return formated_setting


class AccountSQLRepository(AbstractAccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.seen = set()
        self.session = session

    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""
        accounts_: CursorResult = await self.session.execute(
            select(orm.accounts).filter_by(username=username).limit(1)
        )
        account = cast(Account, accounts_.first())
        if account:
            return Ok(
                Account(
                    id=account.id,
                    username=account.username,
                    password=account.password,
                    created_at=account.created_at,
                    status=account.status,
                    email=account.email,
                    lang=account.lang,
                )
            )
        return Err(AccountRepositoryError.user_not_found)

    async def add(self, model: Account) -> AccountOperationResult:
        """Append a new model to the repository."""
        try:
            await self.session.execute(  # type: ignore
                orm.accounts.insert().values(model.dict())  # type: ignore
            )
        except IntegrityError:
            return Err(AccountRepositoryError.integrity_error)
        self.seen.add(model)
        return Ok(...)


class DraftSQLRepository(AbstractDraftRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.seen = set()
        self.session = session

    async def by_id(self, id: str) -> DraftRepositoryResult:
        """Fetch one page by its unique path."""
        qry = (
            select(orm.drafts)
            .join(
                orm.drafts_treepath,
                and_(
                    orm.drafts_treepath.c.ancestor_id == orm.drafts.c.id,
                    orm.drafts_treepath.c.descendant_id == id,
                ),
            )
            .order_by(orm.drafts_treepath.c.length.desc())
        )
        orm_pages: CursorResult = await self.session.execute(qry)
        page: DraftPage | None = None
        orm_page_iter = iter(orm_pages)  # type: ignore
        try:
            orm_page = next(orm_page_iter)  # type: ignore
        except StopIteration:
            return Err(DraftRepositoryError.page_not_found)
        while orm_page:
            typ = resolve_page_type(orm_page.type).unwrap()  # type: ignore
            page = typ(
                id=orm_page.id,
                slug=orm_page.slug,
                title=orm_page.title,
                description=orm_page.description,
                parent=page,
                **orm_page.body,
            )
            try:
                orm_page = next(orm_pages)  # type: ignore
            except StopIteration:
                break

        if page:
            return Ok(page)
        # If we don't have a page here, it means that the tree path is broken
        return Err(DraftRepositoryError.page_broken_treepath)  # coverage: ignore

    async def by_path(self, path: str) -> DraftRepositoryResult:
        """Fetch one page by its unique path."""
        slugs = enumerate(reversed(path.strip("/").split("/")))
        qry = select(orm.drafts)
        for idx, slug in slugs:
            parent = alias(orm.drafts)
            sub = (
                select(orm.drafts_treepath)
                .join(
                    parent,
                    and_(
                        parent.c.id == orm.drafts_treepath.c.ancestor_id,
                        parent.c.slug == slug,
                    ),
                )
                .filter(orm.drafts.c.id == orm.drafts_treepath.c.descendant_id)
                .filter(orm.drafts_treepath.c.length == idx)
            )
            qry = qry.filter(sub.exists())

        page: CursorResult = await self.session.execute(qry)
        p: Any = page.first()
        if p:
            return await self.by_id(p.id)
        return Err(DraftRepositoryError.page_not_found)

    async def by_parent(self, path: Optional[str]) -> DraftSequenceRepositoryResult:
        """Fetch one page by its unique path."""

        if not path:
            # we want roots page here
            sub = ~(
                select(orm.drafts_treepath.c.ancestor_id)
                .filter(orm.drafts.c.id == orm.drafts_treepath.c.descendant_id)
                .filter(orm.drafts_treepath.c.length > 0)
            ).exists()
            parent = None
        else:
            parent_res = await self.by_path(path or "")
            if parent_res.is_err():
                return cast(Err[DraftRepositoryError], parent_res)
            parent = parent_res.unwrap()
            sub = (
                select(orm.drafts_treepath.c.ancestor_id)
                .filter(orm.drafts.c.id == orm.drafts_treepath.c.descendant_id)
                .filter(orm.drafts_treepath.c.length == 1)
                .filter(orm.drafts_treepath.c.ancestor_id == parent.id)
            ).exists()
        qry = select(orm.drafts).filter(sub).order_by(orm.drafts.c.slug)
        pages: CursorResult = await self.session.execute(qry)

        ret: list[DraftPage] = [
            resolve_page_type(p.type).unwrap()(  # type:ignore
                id=p.id,
                slug=p.slug,
                title=p.title,
                description=p.description,
                parent=parent,
                **p.body,
            )
            for p in pages  # type:ignore
        ]
        return Ok(ret)

    async def add(self, model: DraftPage) -> DraftOperationResult:
        """Append a new model to the repository."""

        await self.session.execute(  # type: ignore
            orm.drafts.insert(),  # type: ignore
            [format_draft_page(model)],
        )

        await self.session.execute(  # type: ignore
            orm.drafts_treepath.insert(),  # type: ignore
            [
                {
                    "ancestor_id": model.id,
                    "descendant_id": model.id,
                    "length": 0,
                }
            ],
        )

        # process parents
        if model.parent:
            model.parent.id
            await self.session.execute(
                text(
                    """
                    INSERT INTO drafts_treepath(ancestor_id, descendant_id, length)
                    SELECT
                        drafts_treepath.ancestor_id,
                        :draft_id,
                        drafts_treepath.length + 1
                    FROM drafts_treepath
                    WHERE drafts_treepath.descendant_id = :parent_id
                    """
                ),
                {"draft_id": model.id, "parent_id": model.parent.id},
            )
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: DraftPage) -> DraftOperationResult:
        """Update model in the repository."""
        page = format_draft_page(model)
        page.pop("id")
        cursor: CursorResult = await self.session.execute(
            orm.drafts.update(orm.drafts.c.id == model.id, values=page)  # type: ignore
        )
        if cursor.rowcount == 0:
            return Err(DraftRepositoryError.page_not_found)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: DraftPage) -> DraftOperationResult:
        """Remove the model from the repository."""
        child_pages = await self.by_parent(model.path)
        if child_pages.is_err():
            return cast(Err[DraftRepositoryError], child_pages)

        if child_pages.unwrap():
            return Err(DraftRepositoryError.page_has_children)

        await self.session.execute(
            delete(orm.drafts_treepath).where(
                orm.drafts_treepath.c.descendant_id == model.id
            ),
        )
        await self.session.execute(
            delete(orm.drafts).where(orm.drafts.c.id == model.id),
        )
        self.seen.add(model)
        return Ok(...)


class SnippetSQLRepository(AbstractSnippetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def _format_response(
        self, orm_snippets: CursorResult
    ) -> SnippetRepositoryResult:
        orm_snippet = cast(Snippet, orm_snippets.first())
        if orm_snippet:
            typ: SnippetType = resolve_snippet_type(orm_snippet.type)  # type: ignore
            return Ok(
                typ(
                    id=orm_snippet.id,
                    key=orm_snippet.key,
                    **orm_snippet.body,  # type: ignore
                )
            )
        return Err(SnippetRepositoryError.snippet_not_found)

    async def by_id(self, id: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique id."""
        orm_snippets: CursorResult = await self.session.execute(
            select(orm.snippets).filter_by(id=id).limit(1)
        )
        return await self._format_response(orm_snippets)

    async def by_key(self, key: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique key."""

        orm_snippets: CursorResult = await self.session.execute(
            select(orm.snippets).filter_by(key=key).limit(1)
        )
        return await self._format_response(orm_snippets)

    async def list(self, type: Optional[str] = None) -> SnippetSequenceRepositoryResult:
        """List all snippets, optionally filters on their types."""

        qry = select(orm.snippets)
        if type:
            qry = qry.filter_by(type=type)
        qry = qry.order_by(orm.snippets.c.key)
        orm_snippets: CursorResult = await self.session.execute(qry)
        orm_snippet: Any
        snippets: list[Snippet] = []
        for orm_snippet in orm_snippets:
            typ: SnippetType = resolve_snippet_type(orm_snippet.type)  # type: ignore
            snippets.append(
                typ(
                    id=orm_snippet.id,
                    key=orm_snippet.key,
                    **orm_snippet.body,  # type: ignore
                )
            )
        return Ok(snippets)

    async def add(self, model: Snippet) -> SnippetOperationResult:
        """Append a new model to the repository."""
        qry: Any = orm.snippets.insert().values(format_snippet(model))
        await self.session.execute(qry)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: Snippet) -> SnippetOperationResult:
        """Remove the model from the repository."""
        await self.session.execute(
            delete(orm.snippets).where(orm.snippets.c.key == model.key),
        )
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: Snippet) -> SnippetOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        snippet = format_snippet(model)
        snippet.pop("id")
        qry = orm.snippets.update(  # type: ignore
            orm.snippets.c.id == model.id,  # type: ignore
            values=snippet,
        )
        await self.session.execute(qry)  # type: ignore
        return Ok(...)


class SettingSQLRepository(AbstractSettingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def _format_response(
        self, orm_settings: CursorResult
    ) -> SettingRepositoryResult:
        resp = orm_settings.first()
        if resp:
            typ: SettingType = resolve_setting_type(resp.key)  # type: ignore
            return Ok(
                typ(
                    id=resp.id,  # type: ignore
                    hostname=resp.hostname,  # type: ignore
                    **resp.value,  # type: ignore
                )
            )
        return Err(SettingRepositoryError.setting_not_found)

    async def by_id(self, id: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique id."""
        qry = (
            select(orm.settings, orm.sites.c.hostname)
            .select_from(orm.settings)
            .join(
                orm.sites,
                # orm.sites.c.id == orm.settings.c.site_id,
            )
            .filter(orm.settings.c.id == id)
            .limit(1)
        )
        orm_settings: CursorResult = await self.session.execute(qry)
        return await self._format_response(orm_settings)

    async def by_key(self, hostname: str, key: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique key."""

        orm_settings: CursorResult = await self.session.execute(
            select(orm.settings, orm.sites.c.hostname)
            .select_from(orm.settings)
            .join(
                orm.sites,
                and_(
                    orm.sites.c.id == orm.settings.c.site_id,
                    orm.sites.c.hostname == hostname,
                ),
            )
            .filter(orm.settings.c.key == key)
            .limit(1)
        )
        return await self._format_response(orm_settings)

    async def list(
        self, hostname: Optional[str] = None
    ) -> SettingSequenceRepositoryResult:
        """List all settings, optionally filters on their types."""

        qry = select(orm.settings, orm.sites.c.hostname)
        qry = qry.join(
            orm.sites,
            orm.sites.c.id == orm.settings.c.site_id,
        )
        if hostname:
            qry = qry.filter(orm.sites.c.hostname == hostname)
        qry = qry.order_by(orm.sites.c.hostname, orm.settings.c.key)
        orm_settings: CursorResult = await self.session.execute(qry)
        orm_setting: Any
        settings: list[Setting] = []

        for orm_setting in orm_settings:
            typ: SettingType = resolve_setting_type(orm_setting.key)  # type: ignore
            settings.append(
                typ(
                    id=orm_setting.id,
                    key=orm_setting.key,
                    hostname=orm_setting.hostname,
                    **orm_setting.value,  # type: ignore
                )
            )
        return Ok(settings)

    async def add(self, model: Setting) -> SettingOperationResult:
        """Append a new model to the repository."""
        rsite = await SiteSQLRepository(self.session).by_hostname(model.hostname)
        if rsite.is_err():
            return Err(SettingRepositoryError.site_not_found)
        site_id = rsite.unwrap().id
        qry: Any = orm.settings.insert().values(format_setting(site_id, model))
        await self.session.execute(qry)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: Setting) -> SettingOperationResult:
        """Remove the model from the repository."""
        cursor: CursorResult = await self.session.execute(
            delete(orm.settings).where(orm.settings.c.id == model.id),
        )
        if cursor.rowcount == 0:
            return Err(SettingRepositoryError.setting_not_found)
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: Setting) -> SettingOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        rsite = await SiteSQLRepository(self.session).by_hostname(model.hostname)
        if rsite.is_err():
            return Err(SettingRepositoryError.site_not_found)
        site_id = rsite.unwrap().id
        setting = format_setting(site_id, model)
        setting.pop("id")
        qry = orm.settings.update(  # type: ignore
            orm.settings.c.id == model.id,  # type: ignore
            values=setting,
        )
        await self.session.execute(qry)  # type: ignore
        return Ok(...)


class AuthnTokenSQLRepository(AbstractAuthnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch given token informations from the given token."""
        orm_tokens: CursorResult = await self.session.execute(
            select(orm.authn_tokens).filter_by(token=token).limit(1)
        )
        orm_token = cast(AuthnToken, orm_tokens.first())
        if orm_token:
            return Ok(
                AuthnToken(
                    id=orm_token.id,
                    token=orm_token.token,
                    user_id=orm_token.user_id,
                    created_at=orm_token.created_at,
                    expires_at=orm_token.expires_at,
                    client_addr=str(orm_token.client_addr),
                    user_agent=orm_token.user_agent,
                )
            )
        return Err(AuthnTokenRepositoryError.token_not_found)

    async def add(self, model: AuthnToken) -> AuthnTokenOperationResult:
        """Append a new model to the repository."""
        try:
            await self.session.execute(
                orm.authn_tokens.insert().values(model.dict())  # type: ignore
            )
        except IntegrityError:
            return Err(AuthnTokenRepositoryError.integrity_error)

        return Ok(...)

    async def remove(self, token: str) -> AuthnTokenOperationResult:
        """Delete a new model to the repository."""
        cursor: CursorResult = await self.session.execute(
            delete(orm.authn_tokens).where(orm.authn_tokens.c.token == token),
        )
        if cursor.rowcount == 0:
            return Err(AuthnTokenRepositoryError.token_not_found)
        return Ok(...)


class SiteSQLRepository(AbstractSiteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def list(self) -> SiteSequenceRepositoryResult:
        """Fetch given token informations from the given token."""
        orm_sites: CursorResult = await self.session.execute(
            select(orm.sites).order_by(orm.sites.c.hostname)
        )
        sites: list[Site] = []
        for orm_site in orm_sites:  # type: ignore
            s = cast(Site, orm_site)
            page = await DraftSQLRepository(self.session).by_id(
                s.draft_id  # type: ignore
            )
            page_ok = page.unwrap()

            sites.append(
                Site(
                    id=s.id,
                    draft_id=page_ok.id,
                    root_page_path=page_ok.path,
                    hostname=s.hostname,
                    default=s.default,
                    secure=s.secure,
                )
            )
        return Ok(sites)

    async def add(self, model: Site) -> SiteOperationResult:
        """Append a new model to the repository."""
        data = model.dict()
        data["created_at"] = model.created_at
        rpage = await DraftSQLRepository(self.session).by_path(
            data.pop("root_page_path")
        )
        if rpage.is_err():
            return Err(SiteRepositoryError.root_page_not_found)

        page = rpage.unwrap()  # FIXME, should return Ok(...)
        data["draft_id"] = page.id
        model.draft_id = page.id  # patch if someone use this model
        await self.session.execute(orm.sites.insert().values(data))  # type: ignore
        self.seen.add(model)
        return Ok(...)

    async def _to_site_result(self, orm_sites: CursorResult) -> SiteRepositoryResult:
        orm_site = orm_sites.first()
        if orm_site:
            s = cast(Site, orm_site)
            page = await DraftSQLRepository(self.session).by_id(
                s.draft_id  # type: ignore
            )
            page_ok = page.unwrap()
            return Ok(
                Site(
                    id=s.id,
                    draft_id=page_ok.id,
                    root_page_path=page_ok.path,
                    hostname=s.hostname,
                    default=s.default,
                    secure=s.secure,
                )
            )

        return Err(SiteRepositoryError.site_not_found)

    async def by_id(self, id: str) -> SiteRepositoryResult:
        """Fetch site by id."""
        orm_sites: CursorResult = await self.session.execute(
            select(orm.sites).filter_by(id=id)
        )
        return await self._to_site_result(orm_sites)

    async def by_hostname(self, hostname: str) -> SiteRepositoryResult:
        """Fetch site by hostname."""
        orm_sites: CursorResult = await self.session.execute(
            select(orm.sites).filter_by(hostname=hostname)
        )
        return await self._to_site_result(orm_sites)

    async def update(self, model: Site) -> SiteOperationResult:
        """Update given model into the repository."""
        site = model.dict(exclude={"id", "draft_id", "root_page_path"})

        rpage = await DraftSQLRepository(self.session).by_path(model.root_page_path)
        if rpage.is_err():
            return Err(SiteRepositoryError.root_page_not_found)
        page = rpage.unwrap()  # FIXME, should return Ok(...)
        site["draft_id"] = page.id
        cursor: CursorResult = await self.session.execute(
            orm.sites.update(orm.sites.c.id == model.id, values=site)  # type: ignore
        )
        if cursor.rowcount == 0:
            return Err(SiteRepositoryError.site_not_found)

        return Ok(...)

    async def remove(self, model: Site) -> SiteOperationResult:
        """Remove given model from the repository."""
        await self.session.execute(delete(orm.sites).where(orm.sites.c.id == model.id))
        return Ok(...)


class PageSQLRepository(AbstractPageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def by_draft_page_and_site(
        self, draft_id: str, site_id: str
    ) -> PageRepositoryResult:
        """Fetch one page by its unique id."""

        orm_pages: CursorResult = await self.session.execute(
            select(orm.pages)
            .filter(orm.pages.c.draft_id == draft_id)
            .filter(orm.pages.c.site_id == site_id)
            .limit(1)
        )
        orm_page = cast(Page, orm_pages.first())
        if not orm_page:
            return Err(PageRepositoryError.page_not_found)

        rdraft = await DraftSQLRepository(self.session).by_id(draft_id)
        if rdraft.is_err():
            return Err(PageRepositoryError.page_not_found)
        rsite = await SiteSQLRepository(self.session).by_id(site_id)
        if rsite.is_err():
            return Err(PageRepositoryError.page_not_found)
        return Ok(
            Page(
                id=orm_page.id,
                body=orm_page.body,
                created_at=orm_page.created_at,
                draft=rdraft.unwrap(),
                site=rsite.unwrap(),
                template=orm_page.template,
                type=orm_page.type,
                title=orm_page.title,
                path=orm_page.path,
            )
        )

    async def by_url(self, url: str) -> PageRepositoryResult:
        """Fetch one page by its unique id."""
        url_ = urlparse(url)
        scheme, hostname, path = url_.scheme, url_.netloc, url_.path
        path = f"//{hostname}{path.rstrip('/')}"

        orm_pages: CursorResult = await self.session.execute(
            select(orm.pages).filter(orm.pages.c.path == path).limit(1)
        )
        orm_page = cast(Page, orm_pages.first())
        if not orm_page:
            return Err(PageRepositoryError.page_not_found)

        rdraft = await DraftSQLRepository(self.session).by_id(
            orm_page.draft_id  # type: ignore
        )
        if rdraft.is_err():
            return Err(PageRepositoryError.page_not_found)
        rsite = await SiteSQLRepository(self.session).by_id(
            orm_page.site_id  # type: ignore
        )
        if rsite.is_err():
            return Err(PageRepositoryError.page_not_found)
        site = rsite.unwrap()
        if site.secure and scheme == "http":
            return Err(PageRepositoryError.page_not_found)

        return Ok(
            Page(
                id=orm_page.id,
                body=orm_page.body,
                created_at=orm_page.created_at,
                draft=rdraft.unwrap(),
                site=site,
                template=orm_page.template,
                type=orm_page.type,
                title=orm_page.title,
                path=orm_page.path,
            )
        )

    async def add(self, model: Page) -> PageOperationResult:
        """Append a new model to the repository."""

        await self.session.execute(  # type: ignore
            orm.pages.insert(),  # type: ignore
            [format_page(model)],
        )

        self.seen.add(model)
        return Ok(...)

    async def update(self, model: Page) -> PageOperationResult:
        """Update a model to the repository."""
        page = format_page(model)
        page.pop("id")
        cursor: CursorResult = await self.session.execute(
            orm.pages.update(orm.pages.c.id == model.id, values=page)  # type: ignore
        )
        if cursor.rowcount == 0:
            return Err(PageRepositoryError.page_not_found)
        self.seen.add(model)
        return Ok(...)


class SQLUnitOfWorkBySession(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountSQLRepository(session)
        self.authn_tokens = AuthnTokenSQLRepository(session)
        self.drafts = DraftSQLRepository(session)
        self.pages = PageSQLRepository(session)
        self.sites = SiteSQLRepository(session)
        self.snippets = SnippetSQLRepository(session)
        self.settings = SettingSQLRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def __aenter__(self) -> "SQLUnitOfWorkBySession":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Rollback in case of exception."""
        await super().__aexit__(exc_type, exc, tb)
        if self.session:
            await self.session.close()


async def create_async_session(engine: AsyncEngine) -> Type[AsyncSession]:
    return sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=True,
        autocommit=False,
        expire_on_commit=True,
    )  # type: ignore


class SQLUnitOfWork(AbstractUnitOfWork):
    def __init__(self, settings: Settings) -> None:
        self.app_settings = settings
        self.uow: SQLUnitOfWorkBySession | None = None
        self.create_session: Callable[[], AsyncSession] | None = None
        self.engine: AsyncEngine | None = None

    async def initialize(self) -> None:
        self.engine = create_async_engine(
            self.app_settings.database_url,
            future=True,
            echo=False,
        )
        if self.app_settings.create_database_schema:
            async with self.engine.begin() as conn:  # type: ignore
                await conn.run_sync(orm.metadata.create_all)
        self.create_session = await create_async_session(self.engine)

    async def dispose(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def __aenter__(self) -> AbstractUnitOfWork:
        if self.create_session is None:
            raise RuntimeError("SQLUnitOfWork.initialize() has not been called yet")
        session = self.create_session()
        async with SQLUnitOfWorkBySession(session) as uow:
            return uow

    async def commit(self) -> None:
        raise RuntimeError(
            "Bad usage: use the uow from `async with SQLUnitOfWork(settings) as uow`"
        )

    async def rollback(self) -> None:
        raise RuntimeError(
            "Bad usage: use the uow from `async with SQLUnitOfWork(settings) as uow`"
        )

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """
        Override parent class to do nothing.

        the with decorator instanciate one session and one session handler
        SQLUnitOfWorkBySession.
        """
