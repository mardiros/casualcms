from collections import defaultdict
from operator import and_
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    cast,
)
from urllib.parse import urlparse

from result import Err, Ok
from sqlalchemy import Table, alias, delete, text
from sqlalchemy.engine import Result as SQLResult
from sqlalchemy.engine import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.sql.expression import func

from casualcms.adapters.uow_sqla.setup_database import create_database_schema
from casualcms.config import Settings
from casualcms.domain.model import (
    AbstractPage,
    Account,
    AuthnToken,
    DraftPage,
    Page_contra,
    PublishedPage,
    Setting,
    Setting_contra,
    SettingType,
    Site,
    Snippet,
    Snippet_contra,
    resolve_page_type,
    resolve_setting_type,
    resolve_snippet_type,
)
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


def mapped_result(
    column_descriptions: Sequence[Mapping[str, Any]],
    row: Row[Any],
) -> Mapping[Table, MutableMapping[str, Any]]:
    ret: MutableMapping[Table, Any] = defaultdict(dict)
    for idx, col in enumerate(column_descriptions):
        ret[cast(Table, col["expr"].table)][col["expr"].name] = row[idx]
    return ret


def format_draft_page(page: DraftPage[Any]) -> Dict[str, Any]:
    """Format the page to a dict ready to be inserted in the orm.drafts."""
    p: Dict[str, Any] = page.page.model_dump()
    formated_page: Dict[str, Any] = {
        "id": page.id,
        "type": page.type,
        "created_at": page.created_at,
        "slug": p.pop("slug"),
        "title": p.pop("title"),
        "description": p.pop("description"),
    }
    formated_page["body"] = p
    return formated_page


def format_draft_page_update(page: DraftPage[Any]) -> Dict[str, Any]:
    """Format the page to a dict ready to be inserted in the orm.drafts."""
    p: Dict[str, Any] = page.page.model_dump()
    formated_page: Dict[str, Any] = {
        "id": page.id,
        "type": page.type,
        "created_at": page.created_at,
        "slug": p.pop("slug"),
        "title": p.pop("title"),
        "description": p.pop("description"),
    }
    formated_page["body"] = p
    return formated_page


def format_page(page: PublishedPage[Any]) -> Dict[str, Any]:
    formated_page: Dict[str, Any] = page.model_dump(exclude={"site", "page"})
    formated_page["id"] = page.id
    formated_page["type"] = page.type
    formated_page["title"] = page.title
    formated_page["body"] = page.page.model_dump()
    formated_page["created_at"] = page.created_at
    formated_page["draft_id"] = page.draft_id
    formated_page["site_id"] = page.site.id
    return formated_page


def format_snippet(snippet: Snippet[Any]) -> Dict[str, Any]:
    formated_snippet: Dict[str, Any] = {
        "id": snippet.id,
        "type": snippet.type,
        "created_at": snippet.created_at,
        "key": snippet.key,
        "body": snippet.snippet.model_dump(exclude={"key"}),
    }
    return formated_snippet


def format_setting(site_id: str, setting: Setting[Setting_contra]) -> Dict[str, Any]:
    formated_setting: Dict[str, Any] = {
        "id": setting.id,
        "key": setting.key,
        "created_at": setting.created_at,
        "site_id": site_id,
        "value": setting.setting.model_dump(),
    }
    return formated_setting


def build_parent_path(path: str) -> Iterator[str]:
    path = path.strip("/")
    hostname, *slugs = path.split("/")

    new_path = f"//{hostname}"
    yield new_path
    for slug in slugs:
        new_path = f"{new_path}/{slug}"
        yield new_path


class AccountSQLRepository(AbstractAccountRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.seen = set()
        self.session = session

    async def by_username(self, username: str) -> AccountRepositoryResult:
        """Fetch one user account by its unique username."""
        accounts_: SQLResult[Any] = await self.session.execute(
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
                orm.accounts.insert().values(model.model_dump())  # type: ignore
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
        orm_pages: SQLResult[Any] = await self.session.execute(qry)
        page: AbstractPage | None = None
        draft_page: DraftPage[Any] | None = None
        orm_page_iter = iter(orm_pages)  # type: ignore
        try:
            orm_page = next(orm_page_iter)  # type: ignore
        except StopIteration:
            return Err(DraftRepositoryError.page_not_found)
        while orm_page:
            typ = resolve_page_type(orm_page.type).unwrap()  # type: ignore
            page = typ(
                parent=page,
                slug=orm_page.slug,
                title=orm_page.title,
                description=orm_page.description,
                **orm_page.body,
            )
            draft_page = DraftPage(
                id=orm_page.id,  # type: ignore
                created_at=orm_page.created_at,  # type: ignore
                page=page,
            )
            try:
                orm_page = next(orm_pages)  # type: ignore
            except StopIteration:
                draft_page = DraftPage(
                    id=orm_page.id,  # type: ignore
                    page=page,
                )
                break

        if draft_page:
            return Ok(draft_page)
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

        page: SQLResult[Any] = await self.session.execute(qry)
        p: Any = page.first()
        if p:
            return await self.by_id(p.id)  # type: ignore
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
            parent_page = None
        else:
            parent_res: DraftRepositoryResult = await self.by_path(path or "")
            if parent_res.is_err():
                return cast(Err[DraftRepositoryError], parent_res)
            parent = parent_res.unwrap()
            sub = (
                select(orm.drafts_treepath.c.ancestor_id)
                .filter(orm.drafts.c.id == orm.drafts_treepath.c.descendant_id)
                .filter(orm.drafts_treepath.c.length == 1)
                .filter(orm.drafts_treepath.c.ancestor_id == parent.id)
            ).exists()
            parent_page = parent.page
        qry = select(orm.drafts).filter(sub).order_by(orm.drafts.c.slug)
        pages: SQLResult[Any] = await self.session.execute(qry)

        ret: list[DraftPage[Any]] = [
            DraftPage(
                id=p.id,  # type:ignore
                created_at=p.created_at,  # type:ignore
                page=resolve_page_type(p.type).unwrap()(  # type:ignore
                    parent=parent_page,
                    slug=p.slug,
                    title=p.title,
                    description=p.description,
                    **p.body,
                ),
            )
            for p in pages  # type:ignore
        ]
        return Ok(ret)

    async def add(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Append a new model to the repository."""

        parent_draft = None
        if model.page.parent:
            rparent_draft: DraftRepositoryResult = await self.by_path(
                model.page.parent.metadata.path
            )
            if rparent_draft.is_err():
                return Err(DraftRepositoryError.page_not_found)
            parent_draft = rparent_draft.unwrap()

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
        if parent_draft:
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
                {"draft_id": model.id, "parent_id": parent_draft.id},
            )
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Update model in the repository."""
        page = format_draft_page(model)
        page.pop("id")
        cursor: SQLResult[Any] = await self.session.execute(
            orm.drafts.update().where(orm.drafts.c.id == model.id).values(**page)
        )
        if cursor.rowcount == 0:  # type: ignore
            return Err(DraftRepositoryError.page_not_found)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: DraftPage[Page_contra]) -> DraftOperationResult:
        """Remove the model from the repository."""
        child_pages: DraftSequenceRepositoryResult = await self.by_parent(model.path)
        if child_pages.is_err():
            return cast(Err[DraftRepositoryError], child_pages)

        if child_pages.unwrap():
            return Err(DraftRepositoryError.page_has_children)

        await self.session.execute(
            delete(orm.drafts_treepath).where(
                orm.drafts_treepath.c.descendant_id == model.id  # type: ignore
            ),
        )
        await self.session.execute(
            delete(orm.drafts).where(
                orm.drafts.c.id == model.id,  # type: ignore
            ),
        )
        self.seen.add(model)
        return Ok(...)


class SnippetSQLRepository(AbstractSnippetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def _format_response(
        self, orm_snippets: SQLResult[Any]
    ) -> SnippetRepositoryResult:
        orm_snippet = orm_snippets.first()
        if orm_snippet:
            rtyp = resolve_snippet_type(
                orm_snippet.type,  # type: ignore
            )
            if rtyp.is_err():
                return Err(SnippetRepositoryError.snippet_type_not_found)
            typ = rtyp.unwrap()
            return Ok(
                Snippet(
                    id=orm_snippet.id,  # type: ignore
                    snippet=typ(
                        key=orm_snippet.key,  # type: ignore
                        **orm_snippet.body,  # type: ignore
                    ),
                )
            )
        return Err(SnippetRepositoryError.snippet_not_found)

    async def by_id(self, id: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique id."""
        orm_snippets: SQLResult[Any] = await self.session.execute(
            select(orm.snippets).filter_by(id=id).limit(1)
        )
        return await self._format_response(orm_snippets)  # type: ignore

    async def by_key(self, key: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique key."""

        orm_snippets: SQLResult[Any] = await self.session.execute(
            select(orm.snippets).filter_by(key=key).limit(1)
        )
        return await self._format_response(orm_snippets)  # type: ignore

    async def list(self, type: Optional[str] = None) -> SnippetSequenceRepositoryResult:
        """List all snippets, optionally filters on their types."""

        qry = select(orm.snippets)
        if type:
            qry = qry.filter_by(type=type)
        qry = qry.order_by(orm.snippets.c.key)
        orm_snippets: SQLResult[Any] = await self.session.execute(qry)
        orm_snippet: Any
        snippets: list[Snippet[Any]] = []
        for orm_snippet in orm_snippets:
            rtyp = resolve_snippet_type(orm_snippet.type)  # type: ignore
            # if rtyp.is_err():
            #     return Err(SnippetRepositoryError.snippet_type_not_found)
            typ = rtyp.unwrap()
            snippets.append(
                Snippet(
                    id=orm_snippet.id,  # type: ignore
                    snippet=typ(
                        key=orm_snippet.key,  # type: ignore
                        **orm_snippet.body,  # type: ignore
                    ),
                )
            )
        return Ok(snippets)

    async def add(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Append a new model to the repository."""
        qry: Any = orm.snippets.insert().values(**format_snippet(model))
        await self.session.execute(qry)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Remove the model from the repository."""
        await self.session.execute(
            delete(orm.snippets).where(
                orm.snippets.c.key == model.key,  # type: ignore
            ),
        )
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: Snippet[Snippet_contra]) -> SnippetOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        snippet = format_snippet(model)
        snippet.pop("id")
        qry = (
            orm.snippets.update().where(orm.snippets.c.id == model.id).values(**snippet)
        )
        await self.session.execute(qry)  # type: ignore
        return Ok(...)


class SettingSQLRepository(AbstractSettingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def _format_response(
        self, orm_settings: SQLResult[Any]
    ) -> SettingRepositoryResult:
        resp = orm_settings.first()
        if resp:
            typ: SettingType = resolve_setting_type(resp.key)
            return Ok(
                Setting(
                    id=resp.id,
                    key=resp.key,
                    hostname=resp.hostname,
                    setting=typ(**resp.value),
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
        orm_settings: SQLResult[Any] = await self.session.execute(qry)
        return await self._format_response(orm_settings)  # type: ignore

    async def by_key(self, hostname: str, key: str) -> SettingRepositoryResult:
        """Fetch one setting by its unique key."""

        orm_settings: SQLResult[Any] = await self.session.execute(
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
        return await self._format_response(orm_settings)  # type: ignore

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
        orm_settings: SQLResult[Any] = await self.session.execute(qry)
        orm_setting: Any
        settings: list[Setting[Any]] = []

        for orm_setting in orm_settings:
            typ: SettingType = resolve_setting_type(orm_setting.key)
            settings.append(
                Setting(
                    id=orm_setting.id,
                    key=orm_setting.key,
                    hostname=orm_setting.hostname,
                    setting=typ(**orm_setting.value),
                )
            )
        return Ok(settings)

    async def add(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Append a new model to the repository."""
        rsite = await SiteSQLRepository(self.session).by_hostname(model.hostname)
        if rsite.is_err():
            return Err(SettingRepositoryError.site_not_found)
        site_id = rsite.unwrap().id
        qry: Any = orm.settings.insert().values(
            format_setting(site_id, model)  # type: ignore
        )
        await self.session.execute(qry)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Remove the model from the repository."""
        cursor: SQLResult[Any] = await self.session.execute(
            delete(orm.settings).where(
                orm.settings.c.id == model.id,
            ),
        )
        if cursor.rowcount == 0:  # type: ignore
            return Err(SettingRepositoryError.setting_not_found)
        self.seen.add(model)
        return Ok(...)

    async def update(self, model: Setting[Setting_contra]) -> SettingOperationResult:
        """Update a model from the repository."""
        self.seen.add(model)
        rsite = await SiteSQLRepository(self.session).by_hostname(model.hostname)
        if rsite.is_err():
            return Err(SettingRepositoryError.site_not_found)
        site_id = rsite.unwrap().id
        setting = format_setting(site_id, model)
        setting.pop("id")
        qry = (
            orm.settings.update().where(orm.settings.c.id == model.id).values(**setting)
        )
        await self.session.execute(qry)  # type: ignore
        return Ok(...)


class AuthnTokenSQLRepository(AbstractAuthnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch given token informations from the given token."""
        orm_tokens: SQLResult[Any] = await self.session.execute(
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
                orm.authn_tokens.insert().values(model.model_dump())  # type: ignore
            )
        except IntegrityError:
            return Err(AuthnTokenRepositoryError.integrity_error)

        return Ok(...)

    async def remove(self, token: str) -> AuthnTokenOperationResult:
        """Delete a new model to the repository."""
        cursor: SQLResult[Any] = await self.session.execute(
            delete(orm.authn_tokens).where(
                orm.authn_tokens.c.token == token,  # type: ignore
            ),
        )
        if cursor.rowcount == 0:  # type: ignore
            return Err(AuthnTokenRepositoryError.token_not_found)
        return Ok(...)


class SiteSQLRepository(AbstractSiteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def list(self) -> SiteSequenceRepositoryResult:
        """Fetch given token informations from the given token."""
        orm_sites: SQLResult[Any] = await self.session.execute(
            select(orm.sites).order_by(orm.sites.c.hostname)
        )
        sites: list[Site] = []
        for orm_site in orm_sites:  # type: ignore
            s = cast(Site, orm_site)
            page: DraftRepositoryResult = await DraftSQLRepository(self.session).by_id(
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
        data = model.model_dump()
        data["created_at"] = model.created_at
        rpage: DraftRepositoryResult = await DraftSQLRepository(self.session).by_path(
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

    async def _to_site_result(self, orm_sites: SQLResult[Any]) -> SiteRepositoryResult:
        orm_site = orm_sites.first()
        if orm_site:
            s = cast(Site, orm_site)
            page: DraftRepositoryResult = await DraftSQLRepository(self.session).by_id(
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
        orm_sites: SQLResult[Any] = await self.session.execute(
            select(orm.sites).filter_by(id=id)
        )
        return await self._to_site_result(orm_sites)

    async def by_hostname(self, hostname: str) -> SiteRepositoryResult:
        """Fetch site by hostname."""
        orm_sites: SQLResult[Any] = await self.session.execute(
            select(orm.sites).filter_by(hostname=hostname)
        )
        return await self._to_site_result(orm_sites)

    async def update(self, model: Site) -> SiteOperationResult:
        """Update given model into the repository."""
        site = model.model_dump(exclude={"id", "draft_id", "root_page_path"})

        rpage: DraftRepositoryResult = await DraftSQLRepository(self.session).by_path(
            model.root_page_path
        )
        if rpage.is_err():
            return Err(SiteRepositoryError.root_page_not_found)
        page = rpage.unwrap()  # FIXME, should return Ok(...)
        site["draft_id"] = page.id
        cursor = await self.session.execute(
            orm.sites.update().where(orm.sites.c.id == model.id).values(**site)
        )
        if cursor.rowcount == 0:  # type: ignore
            return Err(SiteRepositoryError.site_not_found)

        return Ok(...)

    async def remove(self, model: Site) -> SiteOperationResult:
        """Remove given model from the repository."""

        await self.session.execute(
            delete(orm.pages).where(
                orm.pages.c.site_id == model.id,
            )
        )
        await self.session.execute(
            delete(orm.settings).where(
                orm.settings.c.site_id == model.id,
            )
        )
        cursor = await self.session.execute(
            delete(orm.sites).where(
                orm.sites.c.id == model.id,
            )
        )
        if cursor.rowcount == 0:  # type: ignore
            return Err(SiteRepositoryError.site_not_found)
        return Ok(...)


class PageSQLRepository(AbstractPageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def by_draft_page_and_site(
        self, draft_id: str, site_id: str
    ) -> PageRepositoryResult:
        """Fetch one page by its unique id."""

        orm_pages: SQLResult[Any] = await self.session.execute(
            select(orm.pages)
            .filter(orm.pages.c.draft_id == draft_id)
            .filter(orm.pages.c.site_id == site_id)
            .limit(1)
        )
        orm_page = orm_pages.first()
        if not orm_page:
            return Err(PageRepositoryError.page_not_found)

        rsite = await SiteSQLRepository(self.session).by_id(site_id)
        if rsite.is_err():
            return Err(PageRepositoryError.page_not_found)

        rtype = resolve_page_type(orm_page.type)  # type: ignore
        if rtype.is_err():
            return Err(PageRepositoryError.page_model_not_found)
        typ = rtype.unwrap()

        return Ok(
            PublishedPage(
                id=orm_page.id,  # type: ignore
                created_at=orm_page.created_at,  # type: ignore
                draft_id=draft_id,
                site=rsite.unwrap(),
                page=typ(**orm_page.body),  # type: ignore
                path=orm_page.path,  # type: ignore
            )
        )

    async def by_url(self, url: str) -> PageRepositoryResult:
        """Fetch one page by its unique id."""
        url_ = urlparse(url)
        scheme, hostname, path = url_.scheme, url_.netloc, url_.path
        path = f"//{hostname}{path.rstrip('/')}"

        qry = (
            select(orm.sites)
            .filter(orm.pages.c.site_id == orm.sites.c.id)
            .filter(orm.pages.c.path == path)
            .order_by(func.length(orm.pages.c.path))
        )

        orm_pages: SQLResult[Any] = await self.session.execute(qry)
        site_row = orm_pages.first()
        if not site_row:
            return Err(PageRepositoryError.page_not_found)

        if site_row.secure and scheme == "http":  # type: ignore
            return Err(PageRepositoryError.page_not_found)

        rdraft: DraftRepositoryResult = await DraftSQLRepository(self.session).by_id(
            site_row.draft_id
        )  # type: ignore
        if rdraft.is_err():
            return Err(PageRepositoryError.page_not_found)
        root = rdraft.unwrap()
        site = Site(root_page_path=root.path, **site_row._asdict())  # type: ignore

        parent_path = list(build_parent_path(path))
        qry = (
            select(orm.pages, orm.sites)
            .filter(orm.pages.c.site_id == orm.sites.c.id)
            .filter(orm.pages.c.path.in_(parent_path))
            .order_by(func.length(orm.pages.c.path))
        )
        orm_pages = await self.session.execute(qry)
        page_result = orm_pages.all()
        parent = None
        published_page = None
        for idx, page_res in enumerate(page_result):
            orm_page = mapped_result(qry.column_descriptions, page_res)[orm.pages]
            rtype = resolve_page_type(orm_page["type"])
            if rtype.is_err():
                return Err(PageRepositoryError.page_model_not_found)
            typ = rtype.unwrap()
            page = typ(site=site, parent=parent, **orm_page["body"])
            if idx == 0:
                page.slug = ""  # type: ignore
            parent = page
            published_page = PublishedPage(
                id=orm_page["id"],
                created_at=orm_page["created_at"],
                draft_id=orm_page["draft_id"],
                path=orm_page["path"],
                site=site,
                page=page,
            )
        if published_page is None:
            # we can't enter this condition, until we have on query for site and pages
            return Err(PageRepositoryError.page_not_found)  # coverage: ignore
        return Ok(published_page)

    async def add(self, model: PublishedPage[Page_contra]) -> PageOperationResult:
        """Append a new model to the repository."""

        await self.session.execute(  # type: ignore
            orm.pages.insert(),  # type: ignore
            [format_page(model)],
        )

        self.seen.add(model)
        return Ok(...)

    async def update(self, model: PublishedPage[Page_contra]) -> PageOperationResult:
        """Update a model to the repository."""
        page = format_page(model)
        page.pop("id")
        cursor: SQLResult[Any] = await self.session.execute(
            orm.pages.update().where(orm.pages.c.id == model.id).values(**page)
        )
        if cursor.rowcount == 0:  # type: ignore
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


async def create_async_session(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        autoflush=True,
        autocommit=False,
        expire_on_commit=True,
    )


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
            await create_database_schema(self.app_settings, self.engine)
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
