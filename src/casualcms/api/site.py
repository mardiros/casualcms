from datetime import datetime
from typing import Annotated, Any, Optional

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSite,
    DeleteSite,
    UpdateSite,
    generate_id,
)
from casualcms.domain.model import AuthnToken, DraftPage, Site
from casualcms.domain.repositories.draft import DraftRepositoryResult

from .base import RESOURCE_UPDATED, HTTPMessage, get_token_info


class PartialSite(BaseModel):
    hostname: str = Field(...)
    default: bool = Field(...)
    secure: bool = Field(...)
    root_page_path: str = Field(...)


async def get_root_draft_by_path(
    root_page_path: str = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> DraftPage[Any]:
    async with app.uow as uow:
        path = root_page_path.strip("/")
        rpage: DraftRepositoryResult = await uow.drafts.by_path(f"/{path}")
        await uow.rollback()
    if rpage.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "root_page_path"], "msg": "Unknown page"}],
        )
    return rpage.unwrap()


async def get_root_draft_by_path_or_none(
    root_page_path: str | None = Body(default=None),
    app: AppConfig = FastAPIConfigurator.depends,
) -> DraftPage[Any] | None:
    if root_page_path is not None:
        return await get_root_draft_by_path(root_page_path, app)
    return None


async def get_site_by_current_hostname(
    current_hostname: str,
    app: AppConfig = FastAPIConfigurator.depends,
) -> Site:
    async with app.uow as uow:
        rsite = await uow.sites.by_hostname(current_hostname)
        await uow.rollback()
    if rsite.is_err():
        raise HTTPException(
            status_code=404,
            detail=[
                {
                    "loc": ["path", "current_hostname"],
                    "msg": rsite.unwrap_err().value,
                }
            ],
        )
    return rsite.unwrap()


async def get_site_by_hostname(
    hostname: str,
    app: AppConfig = FastAPIConfigurator.depends,
) -> Site:
    async with app.uow as uow:
        rsite = await uow.sites.by_hostname(hostname)
        await uow.rollback()
    if rsite.is_err():
        raise HTTPException(
            status_code=404,
            detail=[
                {
                    "loc": ["path", "hostname"],
                    "msg": rsite.unwrap_err().value,
                }
            ],
        )
    return rsite.unwrap()


async def create_site(
    request: Request,
    hostname: str = Body(...),
    default: bool = Body(...),
    secure: bool = Body(...),
    root_page: DraftPage[Any] = Depends(get_root_draft_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> PartialSite:

    cmd = CreateSite(
        id=generate_id(),
        hostname=hostname,
        default=default,
        created_at=datetime.utcnow(),
        root_page_path=root_page.path,
        secure=secure,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rsite = await app.bus.handle(cmd, uow)
        if rsite.is_err():
            raise HTTPException(
                status_code=500,
                detail=[{"loc": ["body", "hostname"], "msg": rsite.unwrap_err().value}],
            )
        await uow.commit()
    site = rsite.unwrap()
    return PartialSite(
        hostname=site.hostname,
        default=site.default,
        root_page_path=site.root_page_path,
        secure=site.secure,
    )


async def update_site(
    request: Request,
    site: Annotated[Site, Depends(get_site_by_current_hostname)],
    root_page: Annotated[
        DraftPage[Any] | None, Depends(get_root_draft_by_path_or_none)
    ],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    default: bool | None = Body(None),
    secure: bool | None = Body(None),
    hostname: str | None = Body(None),
    app: AppConfig = FastAPIConfigurator.depends,
) -> HTTPMessage:

    async with app.uow as uow:
        cmd = UpdateSite(
            id=site.id,
            hostname=hostname,
            default=default,
            root_page_path=root_page.path if root_page else None,
            secure=secure,
        )
        cmd.metadata.clientAddr = request.client.host if request.client else ""
        cmd.metadata.userId = token.user_id

        site = await app.bus.handle(cmd, uow)
        await uow.commit()

    return RESOURCE_UPDATED


async def list_sites(
    request: Request,
    parent: Optional[str] = None,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialSite]:

    async with app.uow as uow:
        sites = await uow.sites.list()
        await uow.rollback()

    if sites.is_err():
        raise HTTPException(
            status_code=500,
            detail=[{"msg": "Internal Server Error"}],
        )

    sites_ok = sites.unwrap()
    return [
        PartialSite(
            hostname=s.hostname,
            default=s.default,
            root_page_path=s.root_page_path,
            secure=s.secure,
        )
        for s in sites_ok
    ]


async def show_site(
    request: Request,
    site: Annotated[Site, Depends(get_site_by_hostname)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
) -> PartialSite:

    return PartialSite(
        hostname=site.hostname,
        default=site.default,
        root_page_path=site.root_page_path,
        secure=site.secure,
    )


async def delete_site(
    request: Request,
    site: Site = Depends(get_site_by_hostname),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    cmd = DeleteSite(
        id=site.id,
        hostname=site.hostname,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "hostname"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return Response(content="", status_code=204)
