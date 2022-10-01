from typing import Any, Mapping, MutableMapping, Optional

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.adapters.jinja2 import Jinja2TemplateRender
from casualcms.domain.messages.commands import CreatePage, DeletePage, UpdatePage
from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.draft import DraftPage, PageType, resolve_page_type
from casualcms.domain.repositories.draft import (
    DraftRepositoryResult,
    DraftSequenceRepositoryResult,
)

from .base import (
    RESOURCE_CREATED,
    RESOURCE_DELETED,
    RESOURCE_UPDATED,
    HTTPMessage,
    MappingWithSlug,
    get_token_info,
)


class PartialPageMeta(BaseModel):
    path: str = Field(...)
    type: str = Field(...)


class PartialPage(BaseModel):
    slug: str = Field(...)
    title: str = Field(...)
    meta: PartialPageMeta = Field(...)


def get_page_type(
    type: str = Body(...),
) -> PageType:
    rpage_type = resolve_page_type(type)
    if rpage_type.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "type"], "msg": rpage_type.unwrap_err().value}],
        )
    return rpage_type.unwrap()


async def build_params(
    payload: MappingWithSlug = Body(...),
    parent: str = Body(None),
    page_type: PageType = Depends(get_page_type),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Mapping[str, Any]:
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {**payload}
        if parent:
            parent_page: DraftRepositoryResult[Any] = await uow.drafts.by_path(parent)
            if parent_page.is_err():
                raise HTTPException(
                    status_code=422,
                    detail=[{"loc": ["body", "parent"], "msg": "Unknown page"}],
                )
            params["parent"] = parent_page.unwrap().page
        try:
            page_type(**params)  # validate pydantic model
        except ValidationError as exc:
            errors = exc.errors()
            for error in errors:
                error["loc"] = ["body", error["loc"]]  # type: ignore
            raise HTTPException(
                status_code=422,
                detail=errors,
            )

        await uow.commit()
    return params


async def create_draft(
    request: Request,
    type: str = Body(...),
    params: Mapping[str, Any] = Depends(build_params),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> HTTPMessage:
    cmd = CreatePage(type=type, payload=params)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rpage = await app.bus.handle(cmd, uow)
        if rpage.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["body", "parent"],
                        "msg": rpage.unwrap_err().value,
                    }
                ],
            )
        await uow.commit()

    return RESOURCE_CREATED


async def list_drafts(
    parent: Optional[str] = None,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialPage]:

    async with app.uow as uow:
        pages: DraftSequenceRepositoryResult[Any] = await uow.drafts.by_parent(parent)
        await uow.rollback()

    if pages.is_err():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["querystring", "parent"],
                    "msg": "Unknown parent",
                }
            ],
        )
    ps = pages.unwrap()
    return [
        PartialPage(
            slug=p.slug,
            title=p.title,
            meta=PartialPageMeta(
                path=p.path,
                type=p.type,
            ),
        )
        for p in ps
    ]


async def draft_by_path(
    path: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> DraftPage[Any]:
    async with app.uow as uow:
        path = path.strip("/")
        rpage: DraftRepositoryResult[Any] = await uow.drafts.by_path(f"/{path}")
        await uow.rollback()
    if rpage.is_err():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["querystring", "path"],
                    "msg": "Unknown page",
                }
            ],
        )
    return rpage.unwrap()


async def show_draft(
    token: AuthnToken = Depends(get_token_info),
    draft_page: DraftPage[Any] = Depends(draft_by_path),
) -> Mapping[str, Any]:
    ret = draft_page.page.dict()
    ret["meta"] = draft_page.page.metadata
    return ret


async def preview_draft(
    request: Request,
    draft_page: DraftPage[Any] = Depends(draft_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    async with app.uow as uow:
        hostname = request.url.hostname or ""
        if request.url.port:
            hostname += f":{request.url.port}"

        renderer = Jinja2TemplateRender(
            uow, app.settings.template_search_path, hostname
        )
        data = await renderer.render_page(
            draft_page.template,
            draft_page.page,
        )
        await uow.rollback()
    return Response(data)


async def update_draft(
    request: Request,
    draft_page: DraftPage[Any] = Depends(draft_by_path),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> HTTPMessage:

    payload.pop("meta", None)
    #  FIXME: validate the payload for the page here
    cmd = UpdatePage(
        id=draft_page.id,
        payload=payload,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        res = await app.bus.handle(cmd, uow)
        if res.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["querystring", "path"],
                        "msg": res.unwrap_err().value,
                    }
                ],
            )
        else:
            await uow.commit()

    return RESOURCE_UPDATED


async def delete_draft(
    request: Request,
    draft_page: DraftPage[Any] = Depends(draft_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:
    cmd = DeletePage(
        id=draft_page.id,
        path=draft_page.path,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["querystring", "path"],
                        "msg": resp.unwrap_err().value,
                    }
                ],
            )
        else:
            await uow.commit()

    return RESOURCE_DELETED
