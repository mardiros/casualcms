from typing import Any

from fastapi import Body, Depends, HTTPException, Request, status
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.adapters.resolver import resolve
from casualcms.domain.messages.commands import CreatePage
from casualcms.domain.model.account import AuthnToken

bearer = HTTPBearer()


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
    return authntoken.unwrap()


async def create_page(
    request: Request,
    type: str = Body(...),
    payload: dict[str, Any] = Body(...),
    parent: str = Body(None),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> dict[str, Any]:
    page_type = resolve(type)  # raise !
    async with app.uow as uow:
        params = {**payload}
        if parent:
            parent_page = await uow.pages.by_path(parent)
            if parent_page.is_err():
                raise HTTPException(
                    status_code=401,
                    detail=[{"loc": ["body", "parent"], "msg": "Unknown page"}],
                )
            params["parent"] = parent_page.unwrap()
        page_type(**params)  # validate pydantic model

    cmd = CreatePage(type=type, payload=params)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = "FIXME"

    async with app.uow as uow:
        page = await app.bus.handle(cmd, uow)

    return {"href": page.path}
