from operator import and_
from typing import Any, Callable, Dict, Optional, Type, cast

from result import Err, Ok
from sqlalchemy import alias, delete, text  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.orm import sessionmaker

from casualcms.config import Settings
from casualcms.domain.model import Account
from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page, resolve_type
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractPageRepository,
)
from casualcms.domain.repositories.authntoken import (
    AuthnTokenRepositoryError,
    AuthnTokenRepositoryResult,
)
from casualcms.domain.repositories.page import (
    PageRepositoryError,
    PageRepositoryResult,
    PageSequenceRepositoryResult,
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
        accounts_ = await self.session.execute(  # type: ignore
            select(orm.accounts).filter_by(username=username).limit(1)
        )
        account: Account = accounts_.first()  # its a Row actually
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
        "id": p.pop("id"),
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
        orm_pages = await self.session.execute(qry)  # type: ignore
        page: Page | None = None
        orm_page_iter = iter(orm_pages)  # type: ignore
        try:
            orm_page = next(orm_page_iter)  # type: ignore
        except StopIteration:
            return Err(PageRepositoryError.page_not_found)
        while orm_page:
            typ = resolve_type(orm_page.type)  # type: ignore
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
        return Err(PageRepositoryError.page_not_found)

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

        page = await self.session.execute(qry)  # type: ignore
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
            parent = await self.by_path(path or "")
            if parent.is_err():
                return cast(Err[PageRepositoryError], parent)
            parent = parent.unwrap()
            sub = (
                select(orm.pages_treepath.c.ancestor_id)
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length == 1)
                .filter(orm.pages_treepath.c.ancestor_id == parent.id)
            ).exists()
        qry = select(orm.pages).filter(sub).order_by(orm.pages.c.slug)
        pages = await self.session.execute(qry)  # type: ignore

        ret: list[Page] = [
            resolve_type(p.type)(  # type:ignore
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
        await self.session.execute(  # type: ignore
            orm.pages.update(orm.pages.c.id == model.id, values=page)  # type: ignore
        )
        self.seen.add(model)


class AuthnTokenSQLRepository(AbstractAuthnRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def by_token(self, token: str) -> AuthnTokenRepositoryResult:
        """Fetch given token informations from the given token."""
        tokens_ = await self.session.execute(  # type: ignore
            select(orm.authn_tokens).filter_by(token=token).limit(1)
        )
        token_: AuthnToken = tokens_.first()  # its a Row actually
        if token_:
            return Ok(
                AuthnToken(
                    id=token_.id,
                    token=token_.token,
                    account_id=token_.account_id,
                    created_at=token_.created_at,
                    expires_at=token_.expires_at,
                    client_addr=str(token_.client_addr),
                    user_agent=token_.user_agent,
                )
            )
        return Err(AuthnTokenRepositoryError.token_not_found)

    async def add(self, model: AuthnToken) -> None:
        """Append a new model to the repository."""
        await self.session.execute(  # type: ignore
            orm.authn_tokens.insert().values(model.dict())  # type: ignore
        )

    async def remove(self, token: str) -> None:
        """Delete a new model to the repository."""
        await self.session.execute(  # type: ignore
            delete(orm.authn_tokens).where(orm.authn_tokens.c.token == token),
        )


class SQLUnitOfWorkBySession:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.accounts = AccountSQLRepository(session)
        self.authn_tokens = AuthnTokenSQLRepository(session)
        self.pages = PageSQLRepository(session)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()


class SQLUnitOfWork(AbstractUnitOfWork):

    create_session: Callable[[], AsyncSession]

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.uow = None
        self.create_session = None  # type: ignore

    async def initialize(self) -> None:
        self.create_session = await create_session(self.settings)

    async def __aenter__(self) -> AbstractUnitOfWork:
        self.session: AsyncSession = self.create_session()
        self.uow = SQLUnitOfWorkBySession(self.session)
        return self

    @property
    def accounts(self):
        if not self.uow:
            raise RuntimeError(".accounts called outside 'async with'")
        return self.uow.accounts

    @property
    def authn_tokens(self):
        if not self.uow:
            raise RuntimeError(".authn_tokens called outside 'async with'")
        return self.uow.authn_tokens

    @property
    def pages(self):
        if not self.uow:
            raise RuntimeError(".pages called outside 'async with'")
        return self.uow.pages

    async def commit(self) -> None:
        if not self.uow:
            raise RuntimeError(".commit() called outside 'async with'")
        await self.uow.commit()
        await self.session.close()

    async def rollback(self) -> None:
        if not self.uow:
            raise RuntimeError(".rollback() called outside 'async with'")
        await self.uow.rollback()
        await self.session.close()


def create_engine(settings: Settings) -> AsyncEngine:
    engine = create_async_engine(
        settings.database_url,
        future=True,
        echo=False,
    )
    return engine


async def create_session(settings: Settings) -> Type[AsyncSession]:
    engine = create_engine(settings)
    async with engine.begin() as conn:  # type: ignore
        await conn.run_sync(orm.metadata.create_all)
    return sessionmaker(engine, class_=AsyncSession)  # type: ignore
