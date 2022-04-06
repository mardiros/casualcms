from typing import Any

from fastapi import Body, Header, HTTPException, Request

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import CreateAuthnToken
from casualcms.domain.model import Account, AccountStatus


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

    cmd = CreateAuthnToken(
        user_id=authenticated_user.id,
        user_agent=user_agent,
    )
    cmd.metadata.clientAddr = request.client.host
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
