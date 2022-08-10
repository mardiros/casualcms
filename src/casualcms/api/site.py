from typing import Optional

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.model import AuthnToken

from .base import get_token_info


class PartialSite(BaseModel):
    hostname: str = Field(...)
    default: bool = Field(...)
    root_page_path: str = Field(...)


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
        )
        for s in sites_ok
    ]
