from typing import Any, MutableMapping, Optional

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreatePage,
    DeletePage,
    UpdatePage,
    generate_id,
)
from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page, resolve_type

from .base import get_token_info


class PartialPageMeta(BaseModel):
    path: str = Field(...)
    type: str = Field(...)


class PartialPage(BaseModel):
    slug: str = Field(...)
    title: str = Field(...)
    meta: PartialPageMeta = Field(...)


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
        params: MutableMapping[str, Any] = {"id": generate_id(), **payload}
        if parent:
            parent_page = await uow.pages.by_path(parent)
            if parent_page.is_err():
                raise HTTPException(
                    status_code=422,
                    detail=[{"loc": ["body", "parent"], "msg": "Unknown page"}],
                )
            params["parent"] = parent_page.unwrap()
        page_type(**params)  # validate pydantic model
        await uow.commit()

    cmd = CreatePage(type=type, payload=params)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id

    async with app.uow as uow:
        page = await app.bus.handle(cmd, uow)
        await uow.commit()

    return {"href": page.path}


async def list_pages(
    request: Request,
    parent: Optional[str] = None,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialPage]:

    async with app.uow as uow:
        pages = await uow.pages.by_parent(parent)
        await uow.rollback()

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
            meta=PartialPageMeta(
                path=p.path,
                type=p.__meta__.type,
            ),
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
        await uow.rollback()

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
        await uow.rollback()

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
        upage: Page = await app.bus.handle(cmd, uow)
        await uow.commit()

    return upage.get_data_context()


async def delete_page(
    request: Request,
    path: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    async with app.uow as uow:
        path = path.strip("/")
        page = await uow.pages.by_path(f"/{path}")
        await uow.rollback()

    if page.is_err():
        return Response(content=page.unwrap_err().value, status_code=404)

    p = page.unwrap()

    cmd = DeletePage(
        id=p.id,
        path=p.path,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "path"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    if page.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "path"], "msg": "Unknown parent"}],
        )

    return Response(content="", status_code=204)
