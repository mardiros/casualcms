from datetime import datetime
from typing import Optional

from fastapi import Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import CreateSite, generate_id
from casualcms.domain.model import AuthnToken

from .base import get_token_info


class PartialSite(BaseModel):
    hostname: str = Field(...)
    default: bool = Field(...)
    secure: bool = Field(...)
    root_page_path: str = Field(...)


async def create_site(
    request: Request,
    hostname: str = Body(...),
    root_page_path: str = Body(...),
    default: bool = Body(...),
    secure: bool = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> PartialSite:

    cmd = CreateSite(
        id=generate_id(),
        hostname=hostname,
        default=default,
        created_at=datetime.utcnow(),
        root_page_path=root_page_path,
        secure=secure,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id

    async with app.uow as uow:
        site = await app.bus.handle(cmd, uow)
        await uow.commit()

    return PartialSite(
        hostname=site.hostname,
        default=site.default,
        root_page_path=site.root_page_path,
        secure=site.secure,
    )


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
