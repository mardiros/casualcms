from typing import Annotated, Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from casualcms.domain.model import (
    AuthnToken,
    SnippetType,
    list_snippet_types,
    resolve_snippet_type,
)
from casualcms.domain.model.fields import SlugField

from .base import get_token_info


def get_snippet_type(type: SlugField) -> SnippetType:
    """Get the snippet type from its key as a non pure function for FastAPI."""
    rtype = resolve_snippet_type(type)
    if rtype.is_err():
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["path", "type"],
                    "msg": rtype.unwrap_err().value,
                },
            ],
        )
    return rtype.unwrap()


class PartialSnippetType(BaseModel):
    type: str = Field(...)
    title: str = Field(...)


async def list_types(
    token: Annotated[AuthnToken, Depends(get_token_info)],
) -> list[PartialSnippetType]:
    stypes = list_snippet_types()
    return sorted(
        [
            PartialSnippetType(
                title=s.__meta__.title,
                type=s.__meta__.type,
            )
            for s in stypes
        ],
        key=lambda s: s.type,
    )


async def show_type(
    type: SlugField,
    token: Annotated[AuthnToken, Depends(get_token_info)],
    snippet_type: Annotated[SnippetType, Depends(get_snippet_type)],
) -> dict[str, Any]:
    jsonschema = snippet_type.schema()
    jsonschema["$defs"].pop("Event", None)
    for key in ("id", "events", "created_at"):
        jsonschema["properties"].pop(key, None)
    return {
        "schema": jsonschema,
        "uiSchema": snippet_type.ui_schema(),
    }
