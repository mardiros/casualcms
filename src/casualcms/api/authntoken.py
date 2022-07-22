from typing import Any

from fastapi import Body, Depends, Header, HTTPException, Request, Response, status

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.api.base import get_token_info
from casualcms.domain.messages.commands import CreateAuthnToken, DeleteAuthnToken
from casualcms.domain.model import Account, AccountStatus
from casualcms.domain.model.account import AuthnToken


async def authenticate(
    request: Request,
    username: str = Body(...),
    password: str = Body(...),
    user_agent: str = Header(None),
    app: AppConfig = FastAPIConfigurator.depends,
) -> dict[str, Any]:

    authenticated_user: Account | None = None
    async with app.uow as uow:
        stored_user = await uow.accounts.by_username(username)
        if stored_user.is_ok():
            user = stored_user.unwrap()
            if user.status == AccountStatus.active and user.match_password(password):
                authenticated_user = user

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail=[
                {"loc": ["body", "username"], "msg": "Invalid username or password"}
            ],
        )

    client_addr: str = request.client.host
    cmd = CreateAuthnToken(
        account_id=authenticated_user.id,
        user_agent=user_agent,
        client_addr=client_addr,
    )
    cmd.metadata.clientAddr = client_addr
    cmd.metadata.userId = authenticated_user.id

    async with app.uow as uow:
        await app.bus.handle(cmd, uow)

    return {
        "token": cmd.token,
        "user_id": authenticated_user.id,
        "username": authenticated_user.username,
        "expires_at": cmd.expires_at,
        "lang": authenticated_user.lang,
    }


async def logout(
    request: Request,
    token: AuthnToken = Depends(get_token_info),
    user_agent: str = Header(None),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Response:
    client_addr: str = request.client.host
    cmd = DeleteAuthnToken(
        token=token.token,
        account_id=token.account_id,
        user_agent=user_agent,
        client_addr=client_addr,
    )
    cmd.metadata.clientAddr = client_addr
    cmd.metadata.userId = token.account_id

    async with app.uow as uow:
        await app.bus.handle(cmd, uow)

    return Response(
        "",
        status_code=status.HTTP_204_NO_CONTENT,
    )
