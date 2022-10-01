from typing import Any

from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreatePage,
    DeletePage,
    PublishPage,
    UpdatePage,
)
from casualcms.domain.model import DraftPage, Page, resolve_page_type
from casualcms.domain.repositories.draft import (
    DraftOperationResult,
    DraftRepositoryResult,
)
from casualcms.domain.repositories.page import (
    PageOperationResult,
    PageRepositoryError,
    PageRepositoryResult,
)
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_page(
    cmd: CreatePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:
    tpage = resolve_page_type(cmd.type).unwrap()
    page = tpage(**cmd.payload)
    draft_page: DraftPage[Any] = DraftPage(
        id=cmd.id, created_at=cmd.created_at, page=page
    )
    return await uow.drafts.add(draft_page)


@listen
async def update_page(
    cmd: UpdatePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:

    rpage: DraftRepositoryResult[Any] = await uow.drafts.by_id(cmd.id)
    if rpage.is_err():
        return Err(rpage.unwrap_err())
    page = rpage.unwrap()
    for key, val in cmd.payload.items():
        setattr(page.page, key, val)
    return await uow.drafts.update(page)


@listen
async def delete_page(
    cmd: DeletePage,
    uow: AbstractUnitOfWork,
) -> DraftOperationResult:

    rpage: DraftRepositoryResult[Any] = await uow.drafts.by_id(cmd.id)
    if rpage.is_err():
        return Err(rpage.unwrap_err())
    page = rpage.unwrap()
    return await uow.drafts.remove(page)


@listen
async def publish_page(
    cmd: PublishPage,
    uow: AbstractUnitOfWork,
) -> PageOperationResult:
    rdraft_page: DraftRepositoryResult[Any] = await uow.drafts.by_id(cmd.id)
    if rdraft_page.is_err():
        return Err(PageRepositoryError.draft_not_found)
    draft_page = rdraft_page.unwrap()

    rsite = await uow.sites.by_id(cmd.site_id)
    if rsite.is_err():
        return Err(PageRepositoryError.site_not_found)

    draft_page = rdraft_page.unwrap()
    site = rsite.unwrap()
    if not draft_page.path.startswith(site.root_page_path):
        return Err(PageRepositoryError.publication_error)
    lprefix = len(site.root_page_path)
    path = draft_page.path[lprefix:]
    path = f"//{site.hostname}{path}"
    rpublished_page: PageRepositoryResult[Any] = await uow.pages.by_draft_page_and_site(
        draft_page.id, site.id
    )
    if rpublished_page.is_ok():
        published_page = rpublished_page.unwrap()
        published_page.path = path
        published_page.page = draft_page.page
        rok = await uow.pages.update(rpublished_page.unwrap())
    else:
        published_page = Page(
            site=site,
            page=draft_page.page,
            draft_id=draft_page.id,
            path=path,
        )
        rok = await uow.pages.add(published_page)
    if rok.is_err():
        return Err(PageRepositoryError.publication_error)
    return Ok(...)
