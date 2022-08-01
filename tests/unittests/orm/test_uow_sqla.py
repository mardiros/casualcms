from types import NoneType
from typing import Any, Sequence

import pytest
from sqlalchemy import text  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy import delete  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.sql.expression import func  # type: ignore

from casualcms.adapters.uow_sqla.uow_sqla import (
    AccountSQLRepository,
    AuthnTokenSQLRepository,
    PageSQLRepository,
)
from casualcms.adapters.uow_sqla import orm
from casualcms.domain.model.page import Page
from .fixtures import fake_account, fake_page, fake_authn_tokens

alice = fake_account(username="alice")
bob = fake_account(username="bob")
dylan = fake_account(username="dylan")
henry = fake_account(username="henry")


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],
            "non_account": henry,
        }
    ],
)
async def test_account_by_username(
    params: Any, sqla_session: AsyncSession, accounts: NoneType
):
    repo = AccountSQLRepository(sqla_session)
    for account in params["accounts"]:
        acc = await repo.by_username(account.username)
        assert acc.is_ok()
        acc_ok = acc.unwrap()
        assert acc_ok.username == account.username
        assert acc_ok.email == acc_ok.email

    acc = await repo.by_username("henry")
    assert acc.is_err()
    err = acc.unwrap_err()
    assert err.name == "user_not_found"


async def test_account_add(sqla_session: AsyncSession):
    repo = AccountSQLRepository(sqla_session)
    acc = fake_account(username="alice")
    await repo.add(acc)
    assert acc in repo.seen
    assert acc in repo.seen

    accounts_ = await sqla_session.execute(  # type: ignore
        text("SELECT username, email FROM accounts where id = :id"), {"id": acc.id}
    )
    account = accounts_.first()  # type: ignore
    assert account.username == "alice"
    assert account.email == acc.email


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(account_id=bob.id)],
        },
    ],
)
async def test_authntoken_by_token(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
    authn_tokens: NoneType,
):
    repo = AuthnTokenSQLRepository(sqla_session)
    tok = await repo.by_token(params["authn_tokens"][0].token)
    assert tok.is_ok()
    tok_ok = tok.unwrap()
    assert tok_ok.id == params["authn_tokens"][0].id
    assert tok_ok.created_at == params["authn_tokens"][0].created_at
    assert tok_ok.expires_at == params["authn_tokens"][0].expires_at
    assert tok_ok.account_id == bob.id
    assert tok_ok.client_addr == "1.2.3.4"
    assert tok_ok.user_agent == "Mozilla/5"

    tok = await repo.by_token("abc")
    assert tok.is_err()
    err = tok.unwrap_err()
    assert err.name == "token_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [bob],  # type: ignore
            "authn_token": fake_authn_tokens(account_id=bob.id),
        },
    ],
)
async def test_authntoken_add(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
):
    repo = AuthnTokenSQLRepository(sqla_session)
    await repo.add(params["authn_token"])
    tok = await repo.by_token(params["authn_token"].token)
    assert tok.is_ok()
    token_ok = tok.unwrap()
    assert token_ok.id == params["authn_token"].id
    await sqla_session.execute(  # type: ignore
        delete(orm.authn_tokens).where(orm.authn_tokens.c.id == token_ok.id),
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(account_id=bob.id)],
        },
    ],
)
async def test_authntoken_delete(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
    authn_tokens: NoneType,
):

    tokens_count = await sqla_session.execute(  # type: ignore
        select(func.count(orm.authn_tokens.c.id)).filter_by(
            token=params["authn_tokens"][0].token
        )
    )
    assert tokens_count.first() == (1,)

    repo = AuthnTokenSQLRepository(sqla_session)
    await repo.remove(params["authn_tokens"][0].token)

    tokens_count = await sqla_session.execute(  # type: ignore
        select(func.count(orm.authn_tokens.c.id)).filter_by(
            token=params["authn_tokens"][0].token
        )
    )
    assert tokens_count.first() == (0,)


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/root",
            "pages": [
                fake_page(
                    type="blog:HomePage",
                    slug="root",
                    hero_title="lorem atchoum",
                )
            ],  # type: ignore
        },
    ],
)
async def test_page_by_path(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    root_page = await repo.by_path(params["path"])
    assert root_page.is_ok()
    rok = root_page.unwrap()
    assert rok.id == params["pages"][0].id
