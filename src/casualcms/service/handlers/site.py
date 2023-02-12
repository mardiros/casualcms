from typing import cast

from result import Err, Ok

from casualcms.domain.messages.commands import CreateSite, DeleteSite, UpdateSite
from casualcms.domain.model import Site
from casualcms.domain.repositories.site import (
    SiteOperationResult,
    SiteRepositoryError,
    SiteRepositoryResult,
)
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_site(
    cmd: CreateSite,
    uow: AbstractUnitOfWork,
) -> SiteRepositoryResult:
    site = Site(
        id=cmd.id,
        created_at=cmd.created_at,
        hostname=cmd.hostname,
        root_page_path=cmd.root_page_path,
        default=cmd.default,
        secure=cmd.secure,
        draft_id=None,  # handled by the repository
    )
    resp = await uow.sites.add(site)
    if resp.is_err():
        return Err(resp.unwrap_err())
    return Ok(site)


@listen
async def update_site(
    cmd: UpdateSite,
    uow: AbstractUnitOfWork,
) -> SiteOperationResult:
    async with uow as uow:
        rsite = await uow.sites.by_id(cmd.id)
        if rsite.is_err():
            return Err(rsite.unwrap_err())
    site = rsite.unwrap()
    if cmd.hostname is not None:
        site.hostname = cmd.hostname
    if cmd.root_page_path is not None:
        site.root_page_path = cmd.root_page_path
    if cmd.default is not None:
        site.default = cmd.default
    if cmd.secure is not None:
        site.secure = cmd.secure
    resp = await uow.sites.update(site)
    return resp


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
