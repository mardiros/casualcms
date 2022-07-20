from typing import Any, Optional

from fastapi import Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import CreatePage, UpdatePage
from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import resolve_type

from .base import get_token_info


class PartialPage(BaseModel):
    slug: str = Field(...)
    title: str = Field(...)
    path: str = Field(...)
    type: str = Field(...)


async def create_page(
    request: Request,
    type: str = Body(...),
    payload: dict[str, Any] = Body(...),
    parent: str = Body(None),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    page_type = resolve_type(type)
    # rtype = resolve(type)
    # if rtype.is_err():
    #     raise HTTPException(
    #         status_code=422,
    #         detail=[{"loc": ["body", "type"], "msg": f"Invalid page type {type}"}],
    #     )
    # page_type = rtype.unwrap()
    async with app.uow as uow:
        params = {**payload}
        if parent:
            parent_page = await uow.pages.by_path(parent)
            if parent_page.is_err():
                raise HTTPException(
                    status_code=422,
                    detail=[{"loc": ["body", "parent"], "msg": "Unknown page"}],
                )
            params["parent"] = parent_page.unwrap()
        page_type(**params)  # validate pydantic model

    cmd = CreatePage(type=type, payload=params)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id

    async with app.uow as uow:
        page = await app.bus.handle(cmd, uow)

    return {"href": page.path}


async def list_pages(
    request: Request,
    parent: Optional[str] = None,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialPage]:

    async with app.uow as uow:
        pages = await uow.pages.by_parent(parent)

    if pages.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "parent"], "msg": "Unknown parent"}],
        )
    ps = pages.unwrap()
    return [
        PartialPage(
            slug=p.slug,
            title=p.title,
            path=p.path,
            type=p.__meta__.type,
        )
        for p in ps
    ]


async def get_page(
    request: Request,
    path: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Any:

    async with app.uow as uow:
        path = path.strip("/")
        page = await uow.pages.by_path(f"/{path}")
    if page.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "path"], "msg": "Unknown parent"}],
        )
    p = page.unwrap()
    return p.get_data_context()


async def update_page(
    request: Request,
    path: str = Field(...),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Any:

    async with app.uow as uow:
        path = path.strip("/")
        page = await uow.pages.by_path(f"/{path}")

    if page.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "path"], "msg": "Unknown parent"}],
        )
    p = page.unwrap()

    cmd = UpdatePage(
        id=p.id,
        payload=payload,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id
    async with app.uow as uow:
        upage = await app.bus.handle(cmd, uow)

    return upage.get_data_context()
