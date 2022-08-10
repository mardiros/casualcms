from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Iterator, Mapping, Sequence

import pytest
import pytest_asyncio
from sqlalchemy import delete, text  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from casualcms.adapters.uow_sqla import orm
from casualcms.adapters.uow_sqla.uow_sqla import SQLUnitOfWork
from casualcms.config import Settings
from casualcms.domain.model.account import Account, AuthnToken
from casualcms.domain.model.page import Page
from casualcms.domain.model.site import Site

DATABASE_URL = "sqlite+aiosqlite:///"


@pytest.fixture()
def bared_sqla_engine() -> Iterator[AsyncEngine]:
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    yield engine


@pytest.fixture()
def app_settings_sqlite() -> Iterator[Settings]:
    template_search_path = str((Path(__file__).parent.parent / "templates").resolve())
    yield Settings(
        template_search_path=template_search_path,
        unit_of_work="casualcms.adapters.uow_sqla:SQLUnitOfWork",
        database_url=DATABASE_URL,
        create_database_schema=True,
        import_models=[],
    )


@pytest_asyncio.fixture()
async def sqla_engine(
    bared_sqla_engine: AsyncEngine,
) -> AsyncGenerator[AsyncEngine, None]:
    async with bared_sqla_engine.begin() as conn:  # type: ignore
        await conn.run_sync(orm.metadata.create_all)

    yield bared_sqla_engine

    async with bared_sqla_engine.begin() as conn:  # type: ignore
        await conn.run_sync(orm.metadata.drop_all)


@pytest.fixture()
def sqla_session(sqla_engine: AsyncEngine) -> Iterator[AsyncSession]:
    async_session = sessionmaker(sqla_engine, class_=AsyncSession)
    yield async_session()  # type: ignore


@pytest_asyncio.fixture()
async def accounts(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    accounts: Sequence[Account] = params["accounts"]
    await sqla_session.execute(  # type: ignore
        orm.accounts.insert(),  # type: ignore
        [a.dict() for a in accounts],
    )
    await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.accounts).where(
            orm.accounts.c.username.in_([a.email for a in accounts])
        ),
    )
    await sqla_session.commit()


@pytest_asyncio.fixture()
async def sites(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    sites: Sequence[Site] = params["sites"]
    await sqla_session.execute(  # type: ignore
        orm.sites.insert(),  # type: ignore
        [s.dict() for s in sites],
    )
    await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.sites).where(orm.sites.c.hostname.in_([s.hostname for s in sites])),
    )
    await sqla_session.commit()


@pytest_asyncio.fixture()
async def authn_tokens(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    authn_tokens: Sequence[AuthnToken] = params["authn_tokens"]
    await sqla_session.execute(  # type: ignore
        orm.authn_tokens.insert(),  # type: ignore
        [t.dict() for t in authn_tokens],
    )
    await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.authn_tokens).where(
            orm.authn_tokens.c.token.in_([t.token for t in authn_tokens])
        ),
    )
    await sqla_session.commit()


@pytest_asyncio.fixture()
async def pages(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:
    def format_page(page: Page) -> Dict[str, Any]:
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

    pages: Sequence[Page] = params["pages"]
    if pages:
        await sqla_session.execute(  # type: ignore
            orm.pages.insert(),  # type: ignore
            [format_page(p) for p in pages],
        )

        await sqla_session.execute(  # type: ignore
            orm.pages_treepath.insert(),  # type: ignore
            [
                {
                    "ancestor_id": p.id,
                    "descendant_id": p.id,
                    "length": 0,
                }
                for p in pages
            ],
        )

        for page in pages:
            # process parents
            if page.parent:
                page.parent.id
                await sqla_session.execute(
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
                    {"page_id": page.id, "parent_id": page.parent.id},
                )

        await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.pages_treepath).where(
            orm.pages_treepath.c.descendant_id.in_([p.id for p in pages])
        ),
    )

    await sqla_session.execute(  # type: ignore
        delete(orm.pages_treepath).where(
            orm.pages_treepath.c.ancestor_id.in_([p.id for p in pages])
        ),
    )

    await sqla_session.execute(  # type: ignore
        delete(orm.pages).where(orm.pages.c.id.in_([p.id for p in pages])),
    )
    await sqla_session.commit()


class DummyAsyncSession:
    def __init__(self):
        self.transaction_state = "begin"

    async def commit(self):
        self.transaction_state += "_commit"

    async def rollback(self):
        self.transaction_state += "_rollback"

    async def close(self):
        self.transaction_state += "_close"

    def get_transaction(self) -> str:  # fake usage
        return self.transaction_state


@pytest.fixture()
def dummy_session():
    return DummyAsyncSession()


@pytest_asyncio.fixture()
async def sql_uow(app_settings_sqlite: Settings) -> AsyncGenerator[SQLUnitOfWork, None]:
    uow = SQLUnitOfWork(app_settings_sqlite)
    await uow.initialize()
    yield uow
    await uow.dispose()


@pytest_asyncio.fixture()
async def accounts_uow(
    sql_uow: SQLUnitOfWork,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    accounts: Sequence[Account] = params["accounts"]
    async with sql_uow as uow:
        for account in accounts:
            await uow.accounts.add(account)
        await uow.commit()

    yield None
    sqla_session = sql_uow.create_session()  # type: ignore
    await sqla_session.execute(  # type: ignore
        delete(orm.accounts).where(
            orm.accounts.c.username.in_([a.email for a in accounts])
        ),
    )
    await sqla_session.commit()
