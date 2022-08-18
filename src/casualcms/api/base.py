from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.model.account import AuthnToken

router = APIRouter()
bearer = HTTPBearer()


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


__all__ = ["router", "get_token_info"]
