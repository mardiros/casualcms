import re
from typing import Any, Callable, Iterator, MutableMapping

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

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


class MappingWithKey(MutableMapping[str, Any]):
    _key_name = "key"

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[Any], MutableMapping[str, Any]]]:
        yield cls.validate

    @classmethod
    def validate(cls, v: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if not isinstance(v, dict):
            raise TypeError("Mapping required")

        if cls._key_name not in v:
            raise ValueError(f"Missing {cls._key_name}")

        m = slug_type_regex.fullmatch(v[cls._key_name])
        if not m:
            raise ValueError(f"Invalid {cls._key_name} field")
        return v

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"


class MappingWithSlug(MappingWithKey):
    _key_name = "slug"


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
