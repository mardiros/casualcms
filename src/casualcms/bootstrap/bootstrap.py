from fastapi import FastAPI

import casualcms.api
import casualcms.service.handlers
import casualcms.ui.backoffice
import casualcms.ui.frontend
from casualcms.adapters.fastapi import FastAPIConfigurator
from casualcms.config import Settings
from casualcms.domain.messages.commands import CreateAccount

from .scanner import scan


def configure(configurator: FastAPIConfigurator) -> None:
    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    # last routes that catch all must ending
    configurator.scan(casualcms.ui.backoffice, categories=["fastapi"])
    configurator.scan(casualcms.ui.frontend, categories=["fastapi"])

    # configure message bus
    configurator.scan(casualcms.service.handlers, categories=["messagebus"])


async def bootstrap(settings: Settings) -> FastAPI:
    with FastAPIConfigurator(settings) as configurator:
        await configurator.initialize()
        configure(configurator)

    app = configurator.app
    if settings.admin_password:
        admin = CreateAccount(
            username=settings.admin_username,
            password=settings.admin_password,
            email=settings.admin_email,
            lang="en",
        )
        async with configurator.config.uow as uow:
            user = await uow.accounts.by_username(settings.admin_username)
            if user:
                await uow.rollback()
            else:
                await configurator.config.bus.handle(
                    admin,
                    uow,
                )
                await uow.commit()

    if settings.import_models:
        scan(*settings.import_models)

    return app
