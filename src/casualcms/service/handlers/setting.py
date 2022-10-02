from typing import Any

from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreateSetting,
    DeleteSetting,
    UpdateSetting,
)
from casualcms.domain.model import Setting, Setting_contra, resolve_setting_type
from casualcms.domain.repositories.setting import (
    SettingOperationResult,
    SettingRepositoryError,
    SettingRepositoryResult,
)
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_setting(
    cmd: CreateSetting,
    uow: AbstractUnitOfWork,
) -> SettingRepositoryResult[Setting_contra]:
    setting_class = resolve_setting_type(cmd.key)
    setting: Setting[Any] = Setting(
        id=cmd.id,
        created_at=cmd.created_at,
        hostname=cmd.hostname,
        key=cmd.key,
        setting=setting_class(
            **cmd.body,
        ),
    )
    rop = await uow.settings.add(setting)
    if rop.is_err():
        return Err(rop.unwrap_err())
    return Ok(setting)


@listen
async def update_setting(
    cmd: UpdateSetting,
    uow: AbstractUnitOfWork,
) -> SettingOperationResult:

    rsetting: SettingRepositoryResult[Any] = await uow.settings.by_id(cmd.id)
    if rsetting.is_err():
        return Err(rsetting.unwrap_err())
    setting = rsetting.unwrap()
    if cmd.body:
        for key, val in cmd.body.items():
            setattr(setting.setting, key, val)
    return await uow.settings.update(setting)


@listen
async def delete_setting(
    cmd: DeleteSetting,
    uow: AbstractUnitOfWork,
) -> SettingOperationResult:
    rsetting: SettingRepositoryResult[Any] = await uow.settings.by_id(cmd.id)
    if rsetting.is_err():
        return Err(SettingRepositoryError.setting_not_found)
    setting = rsetting.unwrap()
    return await uow.settings.remove(setting)
