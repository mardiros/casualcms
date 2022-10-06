from typing import Any

from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, list_setting_types, resolve_setting_type

from .base import get_token_info


class PartialSettingType(BaseModel):
    key: str = Field(...)
    title: str = Field(...)


async def list_types(
    token: AuthnToken = Depends(get_token_info),
) -> list[PartialSettingType]:
    stypes = list_setting_types()
    return sorted(
        [
            PartialSettingType(
                key=s.__meta__.key,
                title=s.__meta__.title,
            )
            for s in stypes
        ],
        key=lambda s: s.key,
    )


async def show_type(
    key: str,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    ptype = resolve_setting_type(key)
    return {
        "schema": ptype.schema(),
        "uiSchema": ptype.ui_schema(),
    }
