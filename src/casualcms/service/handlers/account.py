import bcrypt

from casualcms.domain.messages.commands import CreateAccount
from casualcms.domain.model import Account
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_account(
    cmd: CreateAccount,
    uow: AbstractUnitOfWork,
) -> None:
    password = bcrypt.hashpw(cmd.password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    await uow.accounts.add(
        Account(
            id=cmd.id,
            created_at=cmd.created_at,
            username=cmd.username,
            password=password,
            email=cmd.email,
            lang=cmd.lang,
        ),
    )
