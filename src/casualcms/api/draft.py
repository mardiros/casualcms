from typing import Annotated, Any, Mapping, MutableMapping, Optional

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.adapters.jinja2 import Jinja2TemplateRender
from casualcms.domain.messages.commands import CreatePage, DeletePage, UpdatePage
from casualcms.domain.model import AuthnToken, DraftPage, PageType, resolve_page_type
from casualcms.domain.repositories.draft import (
    DraftRepositoryResult,
    DraftSequenceRepositoryResult,
)

from .base import (
    RESOURCE_CREATED,
    RESOURCE_DELETED,
    RESOURCE_UPDATED,
    HTTPMessage,
    get_token_info,
)


class PartialPageMeta(BaseModel):
    path: str = Field(...)
    type: str = Field(...)
    title: str = Field(...)


class PartialPage(BaseModel):
    slug: str = Field(...)
    title: str = Field(...)
    metadata: PartialPageMeta = Field(...)


def get_page_type(
    type: Annotated[str, Body(...)],
) -> PageType:
    rpage_type = resolve_page_type(type)
    if rpage_type.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "type"], "msg": rpage_type.unwrap_err().value}],
        )
    return rpage_type.unwrap()


async def build_params(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    page_type: Annotated[PageType, Depends(get_page_type)],
    payload: Annotated[Mapping[str, Any], Body(...)],
    parent: Annotated[Optional[str], Body(...)] = None,
) -> Mapping[str, Any]:
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {**payload}
        if parent:
            parent_page: DraftRepositoryResult = await uow.drafts.by_path(parent)
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
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    type: Annotated[str, Body(...)],
    params: Annotated[Mapping[str, Any], Depends(build_params)],
) -> HTTPMessage:
    cmd = CreatePage(type=type, payload=params)
    cmd.metadata.clientAddr = request.client.host if request.client else ""
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
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    parent: str | None = None,
) -> list[PartialPage]:

    async with app.uow as uow:
        pages: DraftSequenceRepositoryResult = await uow.drafts.by_parent(parent)
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
            metadata=PartialPageMeta(
                path=p.path,
                type=p.type,
                title=p.page.__meta__.title,
            ),
        )
        for p in ps
    ]


async def draft_by_path(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    path: str,
) -> DraftPage[Any]:
    async with app.uow as uow:
        path = path.strip("/")
        rpage: DraftRepositoryResult = await uow.drafts.by_path(f"/{path}")
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
    token: Annotated[AuthnToken, Depends(get_token_info)],
    draft_page: Annotated[DraftPage[Any], Depends(draft_by_path)],
) -> Mapping[str, Any]:
    ret = draft_page.page.model_dump()
    ret["metadata"] = draft_page.metadata.model_dump(
        by_alias=False,
        include={
            "type": True,
            "slug": True,
            "path": True,
            "breadcrumb": {
                "items": {
                    "__all__": {
                        "slug": True,
                        "title": True,
                        "path": True,
                    }
                },
            },
        },
    )
    return ret


async def preview_draft(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    draft_page: Annotated[DraftPage[Any], Depends(draft_by_path)],
) -> Response:

    async with app.uow as uow:
        hostname = request.url.hostname or ""
        if request.url.port:
            hostname += f":{request.url.port}"

        renderer = Jinja2TemplateRender(
            uow, app.settings.template_search_path, hostname
        )
        data = await renderer.render_page(draft_page.page)
        await uow.rollback()
    return Response(data)


async def update_draft(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    draft_page: Annotated[DraftPage[Any], Depends(draft_by_path)],
    payload: Annotated[dict[str, Any], Body(...)],
) -> HTTPMessage:

    payload.pop("metadata", None)
    #  FIXME: validate the payload for the page here
    cmd = UpdatePage(
        id=draft_page.id,
        payload=payload,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
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
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    draft_page: Annotated[DraftPage[Any], Depends(draft_by_path)],
) -> Response:
    cmd = DeletePage(
        id=draft_page.id,
        path=draft_page.path,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
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
