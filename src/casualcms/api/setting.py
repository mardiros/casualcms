from typing import Any, Mapping, Sequence

from fastapi import Body, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import (
    CreateSetting,
    DeleteSetting,
    UpdateSetting,
)
from casualcms.domain.model import AuthnToken, resolve_setting_type
from casualcms.domain.model.abstract_setting import Setting_contra
from casualcms.domain.model.setting import PublicMetadata, Setting
from casualcms.domain.repositories.setting import (
    SettingRepositoryResult,
    SettingSequenceRepositoryResult,
)

from .base import get_token_info


class PartialSetting(BaseModel):
    metadata: PublicMetadata = Field(...)


async def validate_payload(
    request: Request,
    hostname: str = Field(...),
    key: str = Body(...),
    payload: dict[str, Any] = Body(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Mapping[str, Any]:
    setting_type = resolve_setting_type(key)
    async with app.uow as uow:
        try:
            setting_type(key=key, **payload)  # validate pydantic model
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
    cmd = CreateSetting(
        key=key,  # type: ignore
        hostname=hostname,
        body=validated_payload,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
    cmd.metadata.userId = token.user_id

    async with app.uow as uow:
        rsetting = await app.bus.handle(cmd, uow)
        if rsetting.is_err():
            raise HTTPException(
                status_code=422,
                detail=[
                    {
                        "loc": ["querystring", "key"],
                        "msg": rsetting.unwrap_err().value,
                    }
                ],
            )
        else:
            setting = rsetting.unwrap()
            await uow.commit()

    return PartialSetting(
        metadata=setting.metadata,
    )


async def list_settings(
    hostname: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Sequence[PartialSetting]:

    async with app.uow as uow:
        settings: SettingSequenceRepositoryResult[Any] = await uow.settings.list(
            hostname=hostname
        )
        await uow.rollback()
    if settings.is_err():
        raise HTTPException(
            status_code=500,
            detail=[{"msg": "Internal Server Error"}],
        )
    setting = settings.unwrap()

    return [PartialSetting(metadata=s.metadata) for s in setting]


async def get_setting_by_path(
    hostname: str = Field(...),
    key: str = Field(...),
    app: AppConfig = FastAPIConfigurator.depends,
) -> Setting[Any]:
    async with app.uow as uow:
        rsetting: SettingRepositoryResult[Any] = await uow.settings.by_key(
            hostname, key
        )
        await uow.rollback()

    if rsetting.is_err():
        raise HTTPException(
            status_code=422,
            detail=[
                {"loc": ["querystring", "key"], "msg": "Unknown setting"},
            ],
        )
    return rsetting.unwrap()


async def show_setting(
    setting: Setting[Setting_contra] = Depends(get_setting_by_path),
    token: AuthnToken = Depends(get_token_info),
) -> Any:
    ret = setting.setting.dict()
    ret["metadata"] = {"key": setting.key, "hostname": setting.hostname}
    return ret


async def update_setting(
    request: Request,
    setting: Setting[Setting_contra] = Depends(get_setting_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    hostname: str = Field(...),
    key: str = Field(...),
    payload: dict[str, Any] = Body(...),
    token: AuthnToken = Depends(get_token_info),
) -> PartialSetting:

    payload.pop("metadata", None)
    cmd = UpdateSetting(
        id=setting.id,
        hostname=hostname,
        key=key,  # type: ignore
        body=payload,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
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

    return PartialSetting(metadata=setting.metadata)


async def delete_setting(
    request: Request,
    setting: Setting[Setting_contra] = Depends(get_setting_by_path),
    app: AppConfig = FastAPIConfigurator.depends,
    token: AuthnToken = Depends(get_token_info),
) -> Response:

    cmd = DeleteSetting(
        id=setting.id,
        hostname=setting.hostname,
        key=setting.key,
    )
    cmd.metadata.clientAddr = request.client.host if request.client else ""
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
