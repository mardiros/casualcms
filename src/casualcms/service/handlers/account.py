from casualcms.domain.messages.commands import CreateAccount
from casualcms.domain.model import Account
from casualcms.service.unit_of_work import AbstractUnitOfWork
from casualcms.service.messagebus import listen


@listen
async def create_account(
    cmd: CreateAccount,
    uow: AbstractUnitOfWork,
) -> None:
    await uow.accounts.add(
        Account(
            id=cmd.id,
            created_at=cmd.created_at,
            username=cmd.username,
            password=cmd.password,
            email=cmd.email,
            lang=cmd.lang,
        ),
    )
