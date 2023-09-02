from typing import Annotated, Any

from fastapi import Body, Depends, Header, HTTPException, Request, Response, status

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.api.base import get_token_info
from casualcms.domain.messages.commands import CreateAuthnToken, DeleteAuthnToken
from casualcms.domain.model import Account, AccountStatus
from casualcms.domain.model.account import AuthnToken


async def get_authenticated_user(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    username: Annotated[str, Body(...)],
    password: Annotated[str, Body(...)],
) -> Account:
    authenticated_user: Account | None = None
    async with app.uow as uow:
        stored_user = await uow.accounts.by_username(username)
        if stored_user.is_ok():
            user = stored_user.unwrap()
            if user.status == AccountStatus.active and user.match_password(password):
                authenticated_user = user
        await uow.rollback()

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail=[
                {"loc": ["body", "username"], "msg": "Invalid username or password"}
            ],
        )
    return authenticated_user


async def authenticate(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    request: Request,
    user_agent: Annotated[str, Header(...)],
    authenticated_user: Annotated[Account, Depends(get_authenticated_user)],
) -> dict[str, Any]:

    client_addr: str = request.client.host if request.client else ""
    cmd = CreateAuthnToken(
        user_id=authenticated_user.id,
        user_agent=user_agent,
        client_addr=client_addr,
    )
    cmd.metadata.clientAddr = client_addr
    cmd.metadata.userId = authenticated_user.id

    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=500,
                detail=[{"loc": ["body", "username"], "msg": "Unknown Error"}],
            )
        await uow.commit()

    token: AuthnToken = resp.unwrap()
    token_dict = token.model_dump(
        exclude={"id", "created_at", "client_addr", "user_agent"}
    )
    token_dict["username"] = authenticated_user.username
    token_dict["lang"] = authenticated_user.lang
    return token_dict


async def logout(
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    request: Request,
    user_agent: Annotated[str, Header(...)],
) -> Response:
    client_addr: str = request.client.host if request.client else ""
    cmd = DeleteAuthnToken(
        token=token.token,
        user_id=token.user_id,
        user_agent=user_agent,
        client_addr=client_addr,
    )
    cmd.metadata.clientAddr = client_addr
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        await app.bus.handle(cmd, uow)
        await uow.commit()

    return Response(
        "",
        status_code=status.HTTP_204_NO_CONTENT,
    )
