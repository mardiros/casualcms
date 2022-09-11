from fastapi import Depends
from pydantic import BaseModel, Field

from casualcms.domain.model import AuthnToken

from .base import get_token_info


class PartialPublishPage(BaseModel):
    href: str = Field(...)


async def publish_page(
    token: AuthnToken = Depends(get_token_info),
) -> PartialPublishPage:
    return PartialPublishPage(href="/")
