from casualcms.domain.messages.commands import CreateSite
from casualcms.domain.model import Site
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
        page_id=None,  # handled by the repository
    )
    await uow.sites.add(site)
    return site
