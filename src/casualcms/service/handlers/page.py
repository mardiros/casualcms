from result import Err

from casualcms.domain.messages.commands import CreatePage, DeletePage, UpdatePage
from casualcms.domain.model.page import resolve_page_type
from casualcms.domain.repositories.page import DraftOperationResult
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_page(
    cmd: CreatePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:
    tpage = resolve_page_type(cmd.type)
    page = tpage(created_at=cmd.created_at, **cmd.payload)
    return await uow.drafts.add(page)


@listen
async def update_page(
    cmd: UpdatePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:

    rpage = await uow.drafts.by_id(cmd.id)
    if rpage.is_err():
        return Err(rpage.unwrap_err())
    page = rpage.unwrap()
    for key, val in cmd.payload.items():
        setattr(page, key, val)
    return await uow.drafts.update(page)


@listen
async def delete_page(
    cmd: DeletePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:

    rpage = await uow.drafts.by_id(cmd.id)
    if rpage.is_err():
        return Err(rpage.unwrap_err())
    page = rpage.unwrap()
    return await uow.drafts.remove(page)
