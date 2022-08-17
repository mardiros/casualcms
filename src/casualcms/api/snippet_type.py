from typing import Any

from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, list_snippet_types, resolve_snippet_type

from .base import get_token_info


class PartialSnippetTemplate(BaseModel):
    type: str = Field(...)


async def list_types(
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialSnippetTemplate]:
    stypes = list_snippet_types()
    return sorted(
        [PartialSnippetTemplate(type=s.__meta__.type) for s in stypes],
        key=lambda s: s.type,
    )


async def show_type(
    type: str,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    ptype = resolve_snippet_type(type)
    jsonschema = ptype.schema()
    jsonschema["definitions"].pop("Event", None)
    for key in ("id", "events", "created_at"):
        jsonschema["properties"].pop(key, None)
    return {
        "schema": jsonschema,
        "uiSchema": ptype.ui_schema(),
    }
