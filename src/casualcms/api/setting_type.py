from typing import Any

from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, list_setting_types, resolve_setting_type

from .base import get_token_info


class PartialSettingType(BaseModel):
    key: str = Field(...)


async def list_types(
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialSettingType]:
    stypes = list_setting_types()
    return sorted(
        [PartialSettingType(key=s.__meta__.key) for s in stypes],
        key=lambda s: s.key,
    )


async def show_type(
    key: str,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    ptype = resolve_setting_type(key)
    jsonschema = ptype.schema()
    jsonschema["required"] = [r for r in jsonschema["required"] if r != "hostname"]
    jsonschema["definitions"].pop("Event", None)
    for key in ("id", "events", "created_at", "hostname"):
        jsonschema["properties"].pop(key, None)
    return {
        "schema": jsonschema,
        "uiSchema": ptype.ui_schema(),
    }
