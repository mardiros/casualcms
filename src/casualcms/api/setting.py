from typing import Any, Mapping, MutableMapping, Sequence

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSetting,
    DeleteSetting,
    UpdateSetting,
    generate_id,
)
from casualcms.domain.model import AuthnToken, resolve_setting_type
from casualcms.domain.model.setting import Setting

from .base import get_token_info


class PartialSettingMeta(BaseModel):
    key: str = Field(...)


class PartialSetting(BaseModel):
    meta: PartialSettingMeta = Field(...)
    hostname: str = Field(...)


async def validate_payload(
    request: Request,
    hostname: str = Field(...),
    key: str = Body(...),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Mapping[str, Any]:
    setting_type = resolve_setting_type(key)
    async with app.uow as uow:
        params: MutableMapping[str, Any] = {
            "id": generate_id(),
            "hostname": hostname,
            **payload,
        }
        try:
            setting_type(**params)  # validate pydantic model
        except ValidationError as exc:
            errors = exc.errors()
            for error in errors:
                error["loc"] = ["body", error["loc"]]  # type: ignore
            raise HTTPException(
                status_code=422,
                detail=errors,
            )
        await uow.rollback()
    return payload


async def create_setting(
    request: Request,
    hostname: str = Field(...),
    key: str = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
    validated_payload: Mapping[str, Any] = Depends(validate_payload),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSetting:
    cmd = CreateSetting(key=key, hostname=hostname, body=validated_payload)
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
        hostname=hostname,
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
        PartialSetting(
            meta=PartialSettingMeta(key=s.__meta__.key),
            hostname=hostname,
        )
        for s in setting
    ]


async def get_setting_by_path(
    hostname: str = Field(...),
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Setting:
    async with app.uow as uow:
        rsetting = await uow.settings.by_key(hostname, key)
        await uow.rollback()

    if rsetting.is_err():
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["querystring", "key"], "msg": "Unknown setting"}],
        )
    return rsetting.unwrap()


async def show_setting(
    setting: Setting = Depends(get_setting_by_path),
    token: AuthnToken = Depends(get_token_info),
) -> Any:
    return setting.get_data_context()


async def update_setting(
    request: Request,
    setting: Setting = Depends(get_setting_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    hostname: str = Field(...),
    key: str = Field(...),
    payload: dict[str, Any] = Body(...),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSetting:

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
                    {"loc": ["querystring", "key"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return PartialSetting(
        meta=PartialSettingMeta(key=setting.__meta__.key),
        hostname=hostname,
    )


async def delete_setting(
    request: Request,
    setting: Setting = Depends(get_setting_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

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
                    {"loc": ["querystring", "key"], "msg": resp.unwrap_err().value}
                ],
            )
        else:
            await uow.commit()

    return Response(content="", status_code=204)
