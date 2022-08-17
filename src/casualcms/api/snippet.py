from typing import Any, MutableMapping

from fastapi import Body, Depends, Request
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import CreateSnippet, generate_id
from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.snippet import resolve_type

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
    snippet_type = resolve_type(type)
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
