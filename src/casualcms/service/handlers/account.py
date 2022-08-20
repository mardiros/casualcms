import bcrypt
from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreateAccount,
    CreateAccountCipheredPassword,
)
from casualcms.domain.model import Account
from casualcms.domain.repositories.user import AccountRepositoryResult
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_account(
    cmd: CreateAccount,
    uow: AbstractUnitOfWork,
) -> AccountRepositoryResult:

    password = bcrypt.hashpw(cmd.password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    account = Account(
        id=cmd.id,
        created_at=cmd.created_at,
        username=cmd.username,
        password=password,
        email=cmd.email,
        lang=cmd.lang,
    )

    resp = await uow.accounts.add(account)
    if resp.is_err():
        return Err(resp.unwrap_err())

    return Ok(account)


@listen
async def create_account_ciphered_password(
    cmd: CreateAccountCipheredPassword,
    uow: AbstractUnitOfWork,
) -> AccountRepositoryResult:
    account = Account(
        id=cmd.id,
        created_at=cmd.created_at,
        username=cmd.username,
        password=cmd.password,
        email=cmd.email,
        lang=cmd.lang,
    )

    resp = await uow.accounts.add(account)
    if resp.is_err():
        return Err(resp.unwrap_err())
    return Ok(account)
