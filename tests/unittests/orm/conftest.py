from typing import Any, AsyncGenerator, Iterator, Mapping, Sequence

import pytest
import pytest_asyncio
from sqlalchemy import delete  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from casualcms.adapters.uow_sqla import orm
from casualcms.domain.model.account import Account, AuthnToken

DATABASE_URL = "sqlite+aiosqlite:///"


@pytest.fixture()
def bared_sqla_engine() -> Iterator[AsyncEngine]:
    engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    yield engine


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
