from typing import Any, MutableMapping, Optional, Sequence

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSnippet,
    DeleteSnippet,
    UpdateSnippet,
    generate_id,
)
from casualcms.domain.model import AuthnToken, resolve_snippet_type

from .base import get_token_info


class PartialSnippetMeta(BaseModel):
    type: str = Field(...)


class PartialSnippet(BaseModel):
    key: str = Field(...)
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
    key = payload.pop("key")
    cmd = CreateSnippet(type=type, key=key, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rsnippet = await app.bus.handle(cmd, uow)
        if rsnippet.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "key"], "msg": rsnippet.unwrap_err().value}
                ],
            )
        else:
            snippet = rsnippet.unwrap()
            await uow.commit()

    return PartialSnippet(
        key=snippet.key,
        meta=PartialSnippetMeta(type=snippet.__meta__.type),
    )


async def list_snippets(
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
    type: Optional[str] = None,
) -> Sequence[PartialSnippet]:

    async with app.uow as uow:
        snippets = await uow.snippets.list(type=type)
        await uow.rollback()
    if snippets.is_err():
        raise HTTPException(status_code=500, detail=[{"msg": "Internal Server Error"}])
    snips = snippets.unwrap()

    return [
        PartialSnippet(key=s.key, meta=PartialSnippetMeta(type=s.__meta__.type))
        for s in snips
    ]


async def show_snippet(
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Any:

    async with app.uow as uow:
        rsnippet = await uow.snippets.by_key(key)
        await uow.rollback()

    if rsnippet.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "key"], "msg": "Unknown snippet"}],
        )
    snippet = rsnippet.unwrap()
    return snippet.get_data_context()


async def update_snippet(
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
    key: str = Field(...),
    payload: dict[str, Any] = Body(...),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSnippet:

    async with app.uow as uow:
        rsnippet = await uow.snippets.by_key(key)
        snippet = rsnippet.unwrap()

    new_key = payload.pop("key")
    payload.pop("meta", None)
    cmd = UpdateSnippet(id=snippet.id, key=new_key, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "key"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return PartialSnippet(
        key=new_key,
        meta=PartialSnippetMeta(type=snippet.__meta__.type),
    )


async def delete_snippet(
    request: Request,
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    async with app.uow as uow:
        key = key.strip("/")
        rsnippet = await uow.snippets.by_key(key)
        await uow.rollback()

    if rsnippet.is_err():
        return Response(content=rsnippet.unwrap_err().value, status_code=404)

    snippet = rsnippet.unwrap()

    cmd = DeleteSnippet(
        id=snippet.id,
        key=snippet.key,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "key"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return Response(content="", status_code=204)
