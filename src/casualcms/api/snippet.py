from typing import Any, MutableMapping, Sequence

from fastapi import Body, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import CreateSnippet, UpdateSnippet, generate_id
from casualcms.domain.model import AuthnToken, resolve_snippet_type

from .base import get_token_info


class PartialSnippetMeta(BaseModel):
    type: str = Field(...)


class PartialSnippet(BaseModel):
    slug: str = Field(...)
    meta: PartialSnippetMeta = Field(...)


async def create_snippet(
    request: Request,
    type: str = Body(...),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> PartialSnippet:
    snippet_type = resolve_snippet_type(type)
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {
            "id": generate_id(),
            "type": type,
            **payload,
        }
        snippet_type(**params)  # validate pydantic model
        await uow.rollback()
    slug = payload.pop("slug")
    cmd = CreateSnippet(type=type, slug=slug, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id

    async with app.uow as uow:
        snippet = await app.bus.handle(cmd, uow)
        await uow.commit()

    return PartialSnippet(
        slug=snippet.slug,
        meta=PartialSnippetMeta(type=snippet.__meta__.type),
    )


async def list_snippets(
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Sequence[PartialSnippet]:

    async with app.uow as uow:
        snippets = await uow.snippets.list()
        await uow.rollback()
    if snippets.is_err():
        raise HTTPException(status_code=500, detail=[{"msg": "Internal Server Error"}])
    snips = snippets.unwrap()

    return [
        PartialSnippet(slug=s.slug, meta=PartialSnippetMeta(type=s.__meta__.type))
        for s in snips
    ]


async def show_snippet(
    slug: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Any:

    async with app.uow as uow:
        rsnippet = await uow.snippets.by_slug(slug)
        await uow.rollback()

    if rsnippet.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "slug"], "msg": "Unknown snippet"}],
        )
    snippet = rsnippet.unwrap()
    return snippet.get_data_context()


async def update_snippet(
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
    slug: str = Field(...),
    payload: dict[str, Any] = Body(...),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSnippet:

    async with app.uow as uow:
        rsnippet = await uow.snippets.by_slug(slug)
        snippet = rsnippet.unwrap()

    new_slug = payload.pop("slug")
    cmd = UpdateSnippet(id=snippet.id, slug=new_slug, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.account_id
    async with app.uow as uow:
        await app.bus.handle(cmd, uow)
        await uow.commit()

    return PartialSnippet(
        slug=new_slug,
        meta=PartialSnippetMeta(type=snippet.__meta__.type),
    )
