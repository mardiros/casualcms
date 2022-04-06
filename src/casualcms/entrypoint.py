import asyncio
from typing import Any

from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

import casualcms.api
import casualcms.service.handlers
import casualcms.ui
from casualcms.adapters.fastapi import FastAPIConfigurator
from casualcms.domain.messages.commands import CreateAccount

SETTINGS: dict[str, str] = {
    "bind": "0.0.0.0:8000",
    "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
    # create an account on startup
    "admin_password": "",  # set it to create an account
    "admin_username": "admin",
    "admin_email": "root@localhost",
}


def configure(configurator: FastAPIConfigurator) -> None:
    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    configurator.scan(casualcms.ui, categories=["fastapi"])

    # configure message bus
    configurator.scan(casualcms.service.handlers, categories=["messagebus"])


async def bootstrap(settings: dict[str, Any]) -> FastAPI:
    with FastAPIConfigurator(settings) as configurator:
        configure(configurator)

    app = configurator.app

    if settings["admin_password"]:
        admin = CreateAccount(
            username=settings["admin_username"],
            password=settings["admin_password"],
            email=settings.get("admin_email", "root@localhost"),
            lang="en",
        )
        async with configurator.config.uow as uow:
            await configurator.config.bus.handle(
                admin,
                uow,
            )
            await uow.commit()

    return app


async def asyncmain(settings: dict[str, Any] = SETTINGS) -> None:
    config = Config()
    complete_settings: dict[str, Any] = settings
    if settings is not SETTINGS:
        complete_settings = SETTINGS.copy()
        complete_settings.update(settings)
    config.bind = complete_settings["bind"].split(",")
    config.use_reloader = complete_settings.get("use_reloader", False)
    app = await bootstrap(complete_settings)
    await serve(app, config)  # type: ignore


def main(settings: dict[str, Any] = SETTINGS) -> None:
    asyncio.run(asyncmain(settings))


if __name__ == "__main__":
    main()
