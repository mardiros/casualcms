from typing import Annotated, Any, Mapping, Sequence

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
    hostname: str,
    key: Annotated[str, Body(...)],
    payload: Annotated[Mapping[str, Any], Body(...)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
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
    token: Annotated[AuthnToken, Depends(get_token_info)],
    hostname: str,
    key: Annotated[str, Body(pattern="^[^/]+$")],
    validated_payload: Annotated[Mapping[str, Any], Depends(validate_payload)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
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
    hostname: str,
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
    token: Annotated[AuthnToken, Depends(get_token_info)],
) -> Sequence[PartialSetting]:

    async with app.uow as uow:
        settings: SettingSequenceRepositoryResult = await uow.settings.list(
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
    hostname: str,
    key: str,
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
) -> Setting[Any]:
    async with app.uow as uow:
        rsetting: SettingRepositoryResult = await uow.settings.by_key(hostname, key)
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
    setting: Annotated[Setting[Setting_contra], Depends(get_setting_by_path)],
    token: Annotated[AuthnToken, Depends(get_token_info)],
) -> Any:
    ret = setting.setting.dict()
    ret["metadata"] = {"key": setting.key, "hostname": setting.hostname}
    return ret


async def update_setting(
    request: Request,
    setting: Annotated[Setting[Setting_contra], Depends(get_setting_by_path)],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    hostname: str,
    key: str,
    payload: Annotated[dict[str, Any], Body(...)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
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
    setting: Annotated[Setting[Setting_contra], Depends(get_setting_by_path)],
    token: Annotated[AuthnToken, Depends(get_token_info)],
    app: Annotated[AppConfig, FastAPIConfigurator.depends],
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
