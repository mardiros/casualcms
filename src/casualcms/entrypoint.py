import asyncio

from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

import casualcms.api
import casualcms.service.handlers
import casualcms.ui
from casualcms.adapters.fastapi import FastAPIConfigurator
from casualcms.config import Settings
from casualcms.domain.messages.commands import CreateAccount


def configure(configurator: FastAPIConfigurator) -> None:
    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    configurator.scan(casualcms.ui, categories=["fastapi"])

    # configure message bus
    configurator.scan(casualcms.service.handlers, categories=["messagebus"])


async def bootstrap(settings: Settings) -> FastAPI:
    with FastAPIConfigurator(settings) as configurator:
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
            await configurator.config.bus.handle(
                admin,
                uow,
            )
            await uow.commit()

    return app


async def asyncmain(settings: Settings) -> None:
    config = Config()
    config.bind = settings.bind.split(",")
    config.use_reloader = settings.use_reloader
    app = await bootstrap(settings)
    await serve(app, config)  # type: ignore


def main() -> None:
    asyncio.run(asyncmain(Settings()))  # type: ignore


if __name__ == "__main__":
    main()
