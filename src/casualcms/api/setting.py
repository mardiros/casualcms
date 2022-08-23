from typing import Any, MutableMapping, Sequence

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSetting,
    DeleteSetting,
    UpdateSetting,
    generate_id,
)
from casualcms.domain.model import AuthnToken, resolve_setting_type

from .base import get_token_info


class PartialSettingMeta(BaseModel):
    key: str = Field(...)


class PartialSetting(BaseModel):
    meta: PartialSettingMeta = Field(...)


async def create_setting(
    request: Request,
    hostname: str = Field(...),
    key: str = Body(...),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> PartialSetting:
    setting_type = resolve_setting_type(key)
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {
            "id": generate_id(),
            "hostname": hostname,
            **payload,
        }
        setting_type(**params)  # validate pydantic model
        await uow.rollback()
    cmd = CreateSetting(key=key, hostname=hostname, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rsetting = await app.bus.handle(cmd, uow)
        if rsetting.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "key"], "msg": rsetting.unwrap_err().value}
                ],
            )
        else:
            setting = rsetting.unwrap()
            await uow.commit()

    return PartialSetting(
        meta=PartialSettingMeta(key=setting.__meta__.key),
    )


async def list_settings(
    hostname: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Sequence[PartialSetting]:

    async with app.uow as uow:
        settings = await uow.settings.list(hostname=hostname)
        await uow.rollback()
    if settings.is_err():
        raise HTTPException(status_code=500, detail=[{"msg": "Internal Server Error"}])
    setting = settings.unwrap()

    return [
        PartialSetting(meta=PartialSettingMeta(key=s.__meta__.key)) for s in setting
    ]


async def show_setting(
    hostname: str = Field(...),
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Any:

    async with app.uow as uow:
        rsetting = await uow.settings.by_key(hostname, key)
        await uow.rollback()

    if rsetting.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "slug"], "msg": "Unknown setting"}],
        )
    setting = rsetting.unwrap()
    return setting.get_data_context()


async def update_setting(
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
    hostname: str = Field(...),
    key: str = Field(...),
    payload: dict[str, Any] = Body(...),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSetting:

    async with app.uow as uow:
        rsetting = await uow.settings.by_key(hostname, key)
        setting = rsetting.unwrap()

    payload.pop("meta", None)
    cmd = UpdateSetting(id=setting.id, hostname=hostname, key=key, body=payload)
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "slug"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return PartialSetting(
        meta=PartialSettingMeta(key=setting.__meta__.key),
    )


async def delete_setting(
    request: Request,
    hostname: str = Field(...),
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    async with app.uow as uow:
        rsetting = await uow.settings.by_key(hostname, key)
        await uow.rollback()

    if rsetting.is_err():
        return Response(content=rsetting.unwrap_err().value, status_code=404)

    setting = rsetting.unwrap()

    cmd = DeleteSetting(
        id=setting.id,
        hostname=setting.hostname,
        key=setting.__meta__.key,
    )
    cmd.metadata.clientAddr = request.client.host
    cmd.metadata.userId = token.user_id
    async with app.uow as uow:
        resp = await app.bus.handle(cmd, uow)
        if resp.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {"loc": ["querystring", "slug"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return Response(content="", status_code=204)
