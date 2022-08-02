from operator import and_
from typing import Any, Optional, cast

from result import Err, Ok
from sqlalchemy import alias, delete  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore

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


class PageSQLRepository(AbstractPageRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.seen = set()
        self.session = session

    async def by_id(self, id: str) -> PageRepositoryResult:
        """Fetch one page by its unique path."""
        pages = await self.session.execute(  # type: ignore
            select(orm.pages).filter_by(id=id).limit(1)
        )
        page: Page = pages.first()  # its a Row actually
        parent_page = None  # FIXME
        if page:
            return Ok(
                Page(
                    id=page.id,
                    slug=page.slug,
                    title=page.title,
                    description=page.description,
                    parent=parent_page,
                )
            )
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
            typ = resolve_type(p.type)
            return Ok(
                typ(
                    id=p.id,
                    slug=p.slug,
                    title=p.title,
                    description=p.description,
                    **p.body,
                )
            )
        return Err(PageRepositoryError.page_not_found)

    async def by_parent(self, path: Optional[str]) -> PageSequenceRepositoryResult:
        """Fetch one page by its unique path."""

        if not path:
            # we want roots here
            """
            select *
            from page
            where not exists (select 1 from from tp where descendant_id = page.id and length > 0)"""
            sub = ~(
                select(orm.pages_treepath.c.ancestor_id)
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length > 0)
            ).exists()
        else:
            parent = await self.by_path(path or "")
            if parent.is_err():
                return cast(Err[PageRepositoryError], parent)
            sub = (
                select(orm.pages_treepath.c.ancestor_id)
                .filter(orm.pages.c.id == orm.pages_treepath.c.descendant_id)
                .filter(orm.pages_treepath.c.length == 1)
                .filter(orm.pages_treepath.c.ancestor_id == parent.unwrap().id)
            ).exists()
        qry = select(orm.pages).filter(sub).order_by(orm.pages.c.slug)
        pages = await self.session.execute(qry)  # type: ignore

        ret: list[Page] = [
            resolve_type(p.type)(  # type:ignore
                id=p.id,
                slug=p.slug,
                title=p.title,
                description=p.description,
                **p.body,
            )
            for p in pages  # type:ignore
        ]
        return Ok(ret)

    async def add(self, model: Page) -> None:
        """Append a new model to the repository."""
        self.seen.add(model)

    async def update(self, model: Page) -> None:
        """Update model in the repository."""
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
                    client_addr=token_.client_addr,
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


class SQLUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountSQLRepository(session)
        self.authn_tokens = AuthnTokenSQLRepository(session)
        self.pages = PageSQLRepository(session)
        self.committed: bool | None = None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False
