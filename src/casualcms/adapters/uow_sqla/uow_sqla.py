from operator import and_
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Type, cast

from result import Err, Ok
from sqlalchemy import alias, delete, text  # type: ignore
from sqlalchemy.engine.cursor import CursorResult  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from casualcms.config import Settings
from casualcms.domain.model import Account, AuthnToken, Page, Site, resolve_page_type
from casualcms.domain.model.snippet import Snippet, SnippetType
from casualcms.domain.model.snippet import resolve_snippet_type
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractPageRepository,
    AbstractSiteRepository,
)
from casualcms.domain.repositories.authntoken import (
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

from . import orm


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

    async def add(self, model: Account) -> None:
        """Append a new model to the repository."""
        await self.session.execute(  # type: ignore
            orm.accounts.insert().values(model.dict())  # type: ignore
        )
        self.seen.add(model)


def format_page(page: Page) -> Dict[str, Any]:
    """Format the page to a dict ready to be inserted in the orm.pages."""
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


class PageSQLRepository(AbstractPageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.seen = set()
        self.session = session

    async def by_id(self, id: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        qry = (
            select(orm.pages)
            .join(
                orm.pages_treepath,
                and_(
                    orm.pages_treepath.c.ancestor_id == orm.pages.c.id,
                    orm.pages_treepath.c.descendant_id == id,
                ),
            )
            .order_by(orm.pages_treepath.c.length.desc())
        )
        orm_pages: CursorResult = await self.session.execute(qry)
        page: Page | None = None
        orm_page_iter = iter(orm_pages)  # type: ignore
        try:
            orm_page = next(orm_page_iter)  # type: ignore
        except StopIteration:
            return Err(PageRepositoryError.page_not_found)
        while orm_page:
            typ = resolve_page_type(orm_page.type)  # type: ignore
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
        return Err(PageRepositoryError.page_broken_treepath)  # coverage: ignore

    async def by_path(self, path: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        slugs = enumerate(reversed(path.strip("/").split("/")))
        qry = select(orm.pages)
        for idx, slug in slugs:
            parent = alias(orm.pages)
            sub = (
                select(orm.pages_treepath)
                .join(
                    parent,
                    and_(
                        parent.c.id == orm.pages_treepath.c.ancestor_id,
                        parent.c.slug == slug,
                    ),
                )
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length == idx)
            )
            qry = qry.filter(sub.exists())

        page: CursorResult = await self.session.execute(qry)
        p: Any = page.first()
        if p:
            return await self.by_id(p.id)
        return Err(PageRepositoryError.page_not_found)

    async def by_parent(self, path: Optional[str]) -> PageSequenceRepositoryResult:
        """Fetch one page by its unique path."""

        if not path:
            # we want roots page here
            sub = ~(
                select(orm.pages_treepath.c.ancestor_id)
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length > 0)
            ).exists()
            parent = None
        else:
            parent_res = await self.by_path(path or "")
            if parent_res.is_err():
                return cast(Err[PageRepositoryError], parent_res)
            parent = parent_res.unwrap()
            sub = (
                select(orm.pages_treepath.c.ancestor_id)
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length == 1)
                .filter(orm.pages_treepath.c.ancestor_id == parent.id)
            ).exists()
        qry = select(orm.pages).filter(sub).order_by(orm.pages.c.slug)
        pages: CursorResult = await self.session.execute(qry)

        ret: list[Page] = [
            resolve_page_type(p.type)(  # type:ignore
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

    async def add(self, model: Page) -> None:
        """Append a new model to the repository."""

        await self.session.execute(  # type: ignore
            orm.pages.insert(),  # type: ignore
            [format_page(model)],
        )

        await self.session.execute(  # type: ignore
            orm.pages_treepath.insert(),  # type: ignore
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
                    INSERT INTO pages_treepath(ancestor_id, descendant_id, length)
                    SELECT
                        pages_treepath.ancestor_id,
                        :page_id,
                        pages_treepath.length + 1
                    FROM pages_treepath
                    WHERE pages_treepath.descendant_id = :parent_id
                    """
                ),
                {"page_id": model.id, "parent_id": model.parent.id},
            )
        self.seen.add(model)

    async def update(self, model: Page) -> None:
        """Update model in the repository."""
        page = format_page(model)
        page.pop("id")
        await self.session.execute(
            orm.pages.update(orm.pages.c.id == model.id, values=page)  # type: ignore
        )
        self.seen.add(model)

    async def remove(self, model: Page) -> PageOperationResult:
        """Remove the model from the repository."""
        child_pages = await self.by_parent(model.path)
        if child_pages.is_err():
            return cast(Err[PageRepositoryError], child_pages)

        if child_pages.unwrap():
            return Err(PageRepositoryError.page_has_children)

        await self.session.execute(
            delete(orm.pages_treepath).where(
                orm.pages_treepath.c.descendant_id == model.id
            ),
        )
        await self.session.execute(
            delete(orm.pages).where(orm.pages.c.id == model.id),
        )
        self.seen.add(model)
        return Ok(...)


class SnippetSQLRepository(AbstractSnippetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.seen = set()

    async def by_slug(self, slug: str) -> SnippetRepositoryResult:
        """Fetch one snippet by its unique slug."""

        orm_snippets: CursorResult = await self.session.execute(
            select(orm.snippets).filter_by(slug=slug).limit(1)
        )
        orm_snippet = cast(Snippet, orm_snippets.first())
        if orm_snippet:
            typ: SnippetType = resolve_snippet_type(orm_snippet.type)  # type: ignore
            return Ok(
                typ(
                    id=orm_snippet.id,
                    slug=orm_snippet.slug,
                    **orm_snippet.body,  # type: ignore
                )
            )
        return Err(SnippetRepositoryError.snippet_not_found)

    async def list(self) -> SnippetSequenceRepositoryResult:
        """Fetch one snippet by its unique slug."""

        orm_snippets: CursorResult = await self.session.execute(
            select(orm.snippets).order_by(orm.snippets.c.slug)
        )
        orm_snippet: Any
        snippets: list[Snippet] = []
        for orm_snippet in orm_snippets:
            typ: SnippetType = resolve_snippet_type(orm_snippet.type)  # type: ignore
            snippets.append(
                typ(
                    id=orm_snippet.id,
                    slug=orm_snippet.slug,
                    **orm_snippet.body,  # type: ignore
                )
            )
        return Ok(snippets)

    async def add(self, model: Snippet) -> SnippetOperationResult:
        """Append a new model to the repository."""
        qry: Any = orm.snippets.insert().values(
            {
                "id": model.id,
                "created_at": model.created_at,
                "type": model.__meta__.type,
                "slug": model.slug,
                "body": model.dict(exclude={"slug"}),
            }
        )
        await self.session.execute(qry)
        self.seen.add(model)
        return Ok(...)

    async def remove(self, model: Snippet) -> SnippetOperationResult:
        """Remove the model from the repository."""
        await self.session.execute(
            delete(orm.snippets).where(orm.snippets.c.slug == model.slug),
        )
        self.seen.add(model)
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
                    account_id=orm_token.account_id,
                    created_at=orm_token.created_at,
                    expires_at=orm_token.expires_at,
                    client_addr=str(orm_token.client_addr),
                    user_agent=orm_token.user_agent,
                )
            )
        return Err(AuthnTokenRepositoryError.token_not_found)

    async def add(self, model: AuthnToken) -> None:
        """Append a new model to the repository."""
        await self.session.execute(
            orm.authn_tokens.insert().values(model.dict())  # type: ignore
        )

    async def remove(self, token: str) -> None:
        """Delete a new model to the repository."""
        await self.session.execute(
            delete(orm.authn_tokens).where(orm.authn_tokens.c.token == token),
        )


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
            page = await PageSQLRepository(self.session).by_id(
                s.page_id  # type: ignore
            )
            page_ok = page.unwrap()

            sites.append(
                Site(
                    id=s.id,
                    page_id=page_ok.id,
                    root_page_path=page_ok.path,
                    hostname=s.hostname,
                    default=s.default,
                    secure=s.secure,
                )
            )
        return Ok(sites)

    async def add(self, model: Site) -> None:
        """Append a new model to the repository."""
        data = model.dict()
        data["created_at"] = model.created_at
        page = await PageSQLRepository(self.session).by_path(data.pop("root_page_path"))

        page_ok = page.unwrap()  # FIXME, should return Ok(...)
        data["page_id"] = page_ok.id
        await self.session.execute(orm.sites.insert().values(data))  # type: ignore
        self.seen.add(model)

    async def _to_site_result(self, orm_sites: CursorResult) -> SiteRepositoryResult:
        orm_site = orm_sites.first()
        if orm_site:
            s = cast(Site, orm_site)
            page = await PageSQLRepository(self.session).by_id(
                s.page_id  # type: ignore
            )
            page_ok = page.unwrap()
            return Ok(
                Site(
                    id=s.id,
                    page_id=page_ok.id,
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

    async def remove(self, model: Site) -> SiteOperationResult:
        await self.session.execute(delete(orm.sites).where(orm.sites.c.id == model.id))
        return Ok(...)


class SQLUnitOfWorkBySession(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountSQLRepository(session)
        self.authn_tokens = AuthnTokenSQLRepository(session)
        self.pages = PageSQLRepository(session)
        self.sites = SiteSQLRepository(session)

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
        self.settings = settings
        self.uow: SQLUnitOfWorkBySession | None = None
        self.create_session: Callable[[], AsyncSession] | None = None
        self.engine: AsyncEngine | None = None

    async def initialize(self) -> None:
        self.engine = create_async_engine(
            self.settings.database_url,
            future=True,
            echo=False,
        )
        if self.settings.create_database_schema:
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
