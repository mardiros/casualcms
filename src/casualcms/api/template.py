from typing import Any
from fastapi import Depends, Query
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, get_available_subtypes
from casualcms.domain.model.page import resolve_type

from .base import get_token_info


class Template(BaseModel):
    type: str = Field(...)


async def list_templates(
    type: str | None = Query(None, description="Filter templates for a parent type"),
    token: AuthnToken = Depends(get_token_info),
) -> list[Template]:
    ptypes = get_available_subtypes(type)
    return sorted(
        [Template(type=p.__meta__.type) for p in ptypes], key=lambda x: x.type
    )


async def show_template(
    type: str,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    ptype = resolve_type(type)
    jsonschema = ptype.schema()
    jsonschema["definitions"].pop("Event", None)
    jsonschema["definitions"].pop("Page", None)
    jsonschema["properties"].pop("events", None)
    jsonschema["properties"].pop("parent", None)
    jsonschema["properties"].pop("created_at", None)
    return {"schema": jsonschema}
