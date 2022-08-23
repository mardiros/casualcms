from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreateSetting,
    DeleteSetting,
    UpdateSetting,
)
from casualcms.domain.model.setting import resolve_setting_type
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
) -> SettingRepositoryResult:
    setting_class = resolve_setting_type(cmd.key)
    setting = setting_class(
        id=cmd.id,
        key=cmd.key,
        hostname=cmd.hostname,
        created_at=cmd.created_at,
        **cmd.body,
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

    rsetting = await uow.settings.by_id(cmd.id)
    if rsetting.is_err():
        return Err(rsetting.unwrap_err())
    setting = rsetting.unwrap()
    if cmd.body:
        for key, val in cmd.body.items():
            setattr(setting, key, val)
    return await uow.settings.update(setting)


@listen
async def delete_setting(
    cmd: DeleteSetting,
    uow: AbstractUnitOfWork,
) -> SettingOperationResult:
    setting = await uow.settings.by_id(cmd.id)
    if setting.is_err():
        return Err(SettingRepositoryError.setting_not_found)
    s = setting.unwrap()
    return await uow.settings.remove(s)
