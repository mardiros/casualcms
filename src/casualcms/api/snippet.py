import logging
from typing import (
    Annotated,
    Any,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    TypedDict,
)

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError
from pydantic.config import ConfigDict

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSnippet,
    DeleteSnippet,
    UpdateSnippet,
    generate_id,
)
from casualcms.domain.model import (
    AuthnToken,
    Snippet,
    SnippetType,
    resolve_snippet_type,
)
from casualcms.domain.model.fields import SlugField
from casualcms.domain.model.snippet import PublicMetadata
from casualcms.domain.repositories.snippet import SnippetRepositoryResult

from .base import get_token_info

log = logging.getLogger(__name__)


class Payload(TypedDict, total=False):
    key: str
    __pydantic_config__ = ConfigDict(extra="allow")  # type: ignore


class PartialSnippet(BaseModel):
    key: str = Field(...)
    metadata: PublicMetadata = Field(...)


def get_snippet_type_body(type: SlugField = Body(...)) -> SnippetType:
    """
    Get the snippet type from its key in the request body,

    as a non pure function for FastAPI."""
    rtype = resolve_snippet_type(type)
    if rtype.is_err():
        raise HTTPException(
            status_code=422,
            detail=[[{"loc": ["body", "type"], "msg": rtype.unwrap_err().value}]],
        )
    return rtype.unwrap()


async def get_snippet_by_key(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    key: str,
) -> Snippet[Any]:
    async with app.uow as uow:
        rsnippet = await uow.snippets.by_key(key)
        if rsnippet.is_err():
            raise HTTPException(
                status_code=404,
                detail=[
                    {
                        "loc": ["path", "hostname"],
                        "msg": rsnippet.unwrap_err().value,
                    }
                ],
            )
        await uow.rollback()

    return rsnippet.unwrap()


async def get_validated_payload(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    payload: Annotated[Mapping[str, Any], Body(...)],
    snippet_type: SnippetType = Depends(get_snippet_type_body),
) -> Mapping[str, Any]:
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {
            "id": generate_id(),
            "type": type,
            **payload,
        }
        try:
            snippet_type(**params)  # validate pydantic model
        except ValidationError as exc:
            errors = exc.errors()
            for error in errors:
                error["loc"] = ["body", ["payload", *error["loc"]]]  # type: ignore
            raise HTTPException(
                status_code=422,
                detail=errors,
            )
        await uow.rollback()
    return payload


async def validate_updated_payload(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    payload: Annotated[Mapping[str, Any], Body(...)],
    snippet: Snippet[Any] = Depends(get_snippet_by_key),
) -> Mapping[str, Any]:
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {
            "id": generate_id(),
            "type": type,
            **payload,
        }
        rtype = resolve_snippet_type(snippet.type)
        if rtype.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["path", "key"],
                        "msg": rtype.unwrap_err().value,
                    }
                ],
            )
        snippet_type = rtype.unwrap()
        try:
            snippet_type(**params)  # validate pydantic model
        except ValidationError as exc:
            errors = exc.errors()
            for error in errors:
                error["loc"] = ["body", ["payload", *error["loc"]]]  # type: ignore
            raise HTTPException(
                status_code=422,
                detail=errors,
            )
        await uow.rollback()
    return payload


async def create_snippet(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    type: Annotated[SlugField, Body()],
    payload: Annotated[Payload, Depends(get_validated_payload)],
) -> PartialSnippet:
    key = payload.pop("key")
    cmd = CreateSnippet(type=type, key=key, body=payload)
    cmd.metadata.clientAddr = request.client.host if request.client else ""
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rsnippet: SnippetRepositoryResult = await app.bus.handle(cmd, uow)
        if rsnippet.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["querystring", "key"],
                        "msg": rsnippet.unwrap_err().value,
                    }
                ],
            )
        else:
            snippet = rsnippet.unwrap()
            await uow.commit()

    return PartialSnippet(
        key=snippet.key,
        metadata=snippet.metadata,
    )


async def list_snippets(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    type: Optional[str] = None,
) -> Sequence[PartialSnippet]:

    async with app.uow as uow:
        snippets = await uow.snippets.list(type=type)
        await uow.rollback()
    if snippets.is_err():
        raise HTTPException(
            status_code=500,
            detail=[{"msg": "Internal Server Error"}],
        )

    snips = snippets.unwrap()
    return [
        PartialSnippet(
            key=s.key,
            metadata=s.metadata,
        )
        for s in snips
    ]


async def show_snippet(
    snippet: Annotated[Snippet[Any], Depends(get_snippet_by_key)],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
) -> Any:
    ret = snippet.snippet.model_dump()
    ret["metadata"] = snippet.metadata
    return ret


async def update_snippet(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    snippet: Annotated[Snippet[Any], Depends(get_snippet_by_key)],
    payload: Annotated[Payload, Depends(validate_updated_payload)],
) -> PartialSnippet:

    new_key = payload.pop("key")
    payload.pop("metadata", None)  # type: ignore
    cmd = UpdateSnippet(id=snippet.id, key=new_key, body=payload)
    cmd.metadata.clientAddr = request.client.host if request.client else ""
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["querystring", "key"],
                        "msg": resp.unwrap_err().value,
                    }
                ],
            )
        else:
            await uow.commit()

    return PartialSnippet(
        key=new_key,
        metadata=snippet.metadata,
    )


async def delete_snippet(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    key: str,
) -> Response:

    async with app.uow as uow:
        key = key.strip("/")
        rsnippet = await uow.snippets.by_key(key)
        await uow.rollback()

    if rsnippet.is_err():
        return Response(
            content=rsnippet.unwrap_err().value,
            status_code=404,
        )

    snippet = rsnippet.unwrap()

    cmd = DeleteSnippet(
        id=snippet.id,
        key=snippet.key,
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
                        "loc": ["querystring", "key"],
                        "msg": resp.unwrap_err().value,
                    }
                ],
            )
        else:
            await uow.commit()

    return Response(content="", status_code=204)
