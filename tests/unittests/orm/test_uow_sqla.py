from types import NoneType
from typing import Any

import pytest
from sqlalchemy import text  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from casualcms.adapters.uow_sqla.uow_sqla import AccountSQLRepository

from .fixtures import fake_account


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [
                fake_account(username="alice"),
                fake_account(username="bob"),
                fake_account(username="dylan"),
            ],
            "non_account": fake_account(username="henry"),
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
