from typing import cast

from result import Err

from casualcms.domain.messages.commands import CreatePage, DeletePage, UpdatePage
from casualcms.domain.model.page import Page, resolve_page_type
from casualcms.domain.repositories.page import PageOperationResult, PageRepositoryError
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_page(
    cmd: CreatePage,
    uow: AbstractUnitOfWork,
) -> Page:
    tpage = resolve_page_type(cmd.type)
    page = tpage(created_at=cmd.created_at, **cmd.payload)
    await uow.pages.add(page)
    return page


@listen
async def update_page(
    cmd: UpdatePage,
    uow: AbstractUnitOfWork,
) -> Page:

    async with uow as uow:
        page = await uow.pages.by_id(cmd.id)
        p = page.unwrap()
        for key, val in cmd.payload.items():
            setattr(p, key, val)
        await uow.pages.update(p)
    return p


@listen
async def delete_page(
    cmd: DeletePage,
    uow: AbstractUnitOfWork,
) -> PageOperationResult:

    async with uow as uow:
        page = await uow.pages.by_id(cmd.id)
        if page.is_err():
            return cast(Err[PageRepositoryError], page)
        p = page.unwrap()
        resp = await uow.pages.remove(p)
    return resp
