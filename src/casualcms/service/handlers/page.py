from casualcms.domain.messages.commands import CreatePage
from casualcms.domain.model.page import Page, resolve_type
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_page(
    cmd: CreatePage,
    uow: AbstractUnitOfWork,
) -> Page:
    tpage = resolve_type(cmd.type)
    page = tpage(created_at=cmd.created_at, **cmd.payload)
    await uow.pages.add(
        page,
    )
    return page
