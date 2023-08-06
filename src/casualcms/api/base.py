import re

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.model.account import AuthnToken

__all__ = [
    "router",
    "get_token_info",
    "MappingWithKey",
    "MappingWithSlug",
    "RESOURCE_CREATED",
    "RESOURCE_UPDATED",
    "RESOURCE_DELETED",
]

router = APIRouter()
bearer = HTTPBearer()

slug_type_regex = re.compile("^[^/]+$")


class MappingWithKey(BaseModel):
    key: str = Field(...)
    model_config = ConfigDict(extra="allow")


class MappingWithSlug(BaseModel):
    slug: str = Field(...)
    model_config = ConfigDict(extra="allow")


class HTTPMessage(BaseModel):
    message: str = Field(...)


RESOURCE_CREATED = HTTPMessage(message="Resource Created")
RESOURCE_UPDATED = HTTPMessage(message="Resource Updated")
RESOURCE_DELETED = Response(content="", status_code=204)


async def get_token_info(
    token: HTTPAuthorizationCredentials = Depends(bearer),
    app: AppConfig = FastAPIConfigurator.depends,
) -> AuthnToken:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    async with app.uow as uow:
        authntoken = await uow.authn_tokens.by_token(token.credentials)
        if authntoken.is_err():
            raise credentials_exception
        await uow.commit()
    return authntoken.unwrap()
