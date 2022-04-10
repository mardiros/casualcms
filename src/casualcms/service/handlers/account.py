import bcrypt

from casualcms.domain.messages.commands import (
    CreateAccount,
    CreateAccountCipheredPassword,
)
from casualcms.domain.model import Account
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_account(
    cmd: CreateAccount,
    uow: AbstractUnitOfWork,
) -> Account:

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

    await uow.accounts.add(account)
    return account


@listen
async def create_account_ciphered_password(
    cmd: CreateAccountCipheredPassword,
    uow: AbstractUnitOfWork,
) -> Account:
    account = Account(
        id=cmd.id,
        created_at=cmd.created_at,
        username=cmd.username,
        password=cmd.password,
        email=cmd.email,
        lang=cmd.lang,
    )

    await uow.accounts.add(account)
    return account
