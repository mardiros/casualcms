from typing import Any

from fastapi import Body, Depends, HTTPException
from result import Result

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator
from casualcms.domain.messages.commands import PublishPage
from casualcms.domain.model import AuthnToken, PublishedPage
from casualcms.domain.repositories.draft import DraftRepositoryResult

from .base import RESOURCE_CREATED, HTTPMessage, get_token_info


async def publish_page(
    hostname: str = Body(...),
    path: str = Body(...),
    token: AuthnToken = Depends(get_token_info),
    app: AppConfig = FastAPIConfigurator.depends,
) -> HTTPMessage:

    async with app.uow as uow:
        errs = []
        rdraft: DraftRepositoryResult = await uow.drafts.by_path(path)
        if rdraft.is_err():
            errs.append([{"loc": ["body", "path"], "msg": rdraft.unwrap_err().value}])
        rsite = await uow.sites.by_hostname(hostname)
        if rsite.is_err():
            errs.append(
                [{"loc": ["body", "hostname"], "msg": rsite.unwrap_err().value}]
            )
        if errs:
            raise HTTPException(status_code=422, detail=errs)
        draft = rdraft.unwrap()
        site = rsite.unwrap()

        cmd = PublishPage(id=draft.id, site_id=site.id)
        rppage: Result[PublishedPage[Any], bool] = await app.bus.handle(cmd, uow)
        if rppage.is_err():
            raise HTTPException(
                status_code=500, detail={"msg": "Internal Server Error"}
            )
        await uow.commit()

    return RESOURCE_CREATED
