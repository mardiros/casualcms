from typing import Any

from fastapi import Body, Header, HTTPException, Request

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.adapters.resolver import resolve
from casualcms.domain.messages.commands import CreatePage


async def create_page(
    request: Request,
    type: str = Body(...),
    payload: dict[str, Any] = Body(...),
    parent: str = Body(None),
    user_agent: str = Header(None),
    app: AppConfig = FastAPIConfigurator.depends,
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
