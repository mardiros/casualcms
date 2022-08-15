from typing import cast

from result import Err

from casualcms.domain.messages.commands import CreateSite, DeleteSite
from casualcms.domain.model import Site
from casualcms.domain.repositories.site import SiteOperationResult, SiteRepositoryError
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_site(
    cmd: CreateSite,
    uow: AbstractUnitOfWork,
) -> Site:
    site = Site(
        id=cmd.id,
        created_at=cmd.created_at,
        hostname=cmd.hostname,
        root_page_path=cmd.root_page_path,
        default=cmd.default,
        secure=cmd.secure,
        page_id=None,  # handled by the repository
    )
    await uow.sites.add(site)
    return site


@listen
async def delete_site(
    cmd: DeleteSite,
    uow: AbstractUnitOfWork,
) -> SiteOperationResult:

    async with uow as uow:
        site = await uow.sites.by_id(cmd.id)
        if site.is_err():
            return cast(Err[SiteRepositoryError], site)
    s = site.unwrap()
    resp = await uow.sites.remove(s)
    return resp
