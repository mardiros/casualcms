from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreatePage,
    DeletePage,
    PublishPage,
    UpdatePage,
)
from casualcms.domain.model import Page, resolve_page_type
from casualcms.domain.repositories.draft import DraftOperationResult
from casualcms.domain.repositories.page import PageOperationResult, PageRepositoryError
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


@listen
async def publish_page(
    cmd: PublishPage,
    uow: AbstractUnitOfWork,
) -> PageOperationResult:
    rpage = await uow.drafts.by_id(cmd.id)
    if rpage.is_err():
        return Err(PageRepositoryError.draft_not_found)
    page = rpage.unwrap()

    rsite = await uow.sites.by_id(cmd.site_id)
    if rsite.is_err():
        return Err(PageRepositoryError.site_not_found)

    page = rpage.unwrap()
    site = rsite.unwrap()
    if not page.path.startswith(site.root_page_path):
        return Err(PageRepositoryError.publication_error)
    path = page.path[len(site.root_page_path) :]
    path = f"//{site.hostname}/{path}"
    rpublished_page = await uow.pages.by_page_and_site(page.id, site.id)
    if rpublished_page.is_ok():
        published_page = rpublished_page.unwrap()
        published_page.template = page.get_template()
        published_page.title = page.title
        published_page.path = path
        published_page.body = page.get_context()
        rok = await uow.pages.update(rpublished_page.unwrap())
    else:
        published_page = Page(
            site=site,
            page=page,
            type=page.__meta__.type,
            template=page.get_template(),
            title=page.title,
            path=path,
            body=page.get_context(),
        )
        rok = await uow.pages.add(published_page)
    if rok.is_err():
        return Err(PageRepositoryError.publication_error)
    return Ok(...)
