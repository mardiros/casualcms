from typing import Any

from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, list_snippet_types
from casualcms.domain.model.snippet import SnippetKey, SnippetType

from .base import get_snippet_type, get_token_info


class PartialSnippetType(BaseModel):
    type: str = Field(...)


async def list_types(
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialSnippetType]:
    stypes = list_snippet_types()
    return sorted(
        [PartialSnippetType(type=s.__meta__.type) for s in stypes],
        key=lambda s: s.type,
    )


async def show_type(
    type: SnippetKey,
    token: AuthnToken = Depends(get_token_info),
    snippet_type: SnippetType = Depends(get_snippet_type),
) -> dict[str, Any]:
    jsonschema = snippet_type.schema()
    jsonschema["definitions"].pop("Event", None)
    for key in ("id", "events", "created_at"):
        jsonschema["properties"].pop(key, None)
    return {
        "schema": jsonschema,
        "uiSchema": snippet_type.ui_schema(),
    }
