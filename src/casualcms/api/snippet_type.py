from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken, list_snippet_types

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
