from fastapi import Depends, Query
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, get_available_subtypes

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
