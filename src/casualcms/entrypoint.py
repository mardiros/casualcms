import asyncio
from typing import Any

from fastapi import FastAPI

from hypercorn.asyncio import serve
from hypercorn.config import Config

import casualcms.api
import casualcms.ui
import casualcms.service.handlers
from casualcms.adapters.fastapi import FastAPIConfigurator


SETTINGS: dict[str, str] = {
    "server_host": "0.0.0.0:8000",
    "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
}


def configure(configurator: FastAPIConfigurator):
    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    configurator.scan(casualcms.ui, categories=["fastapi"])

    # configure message bus
    configurator.scan(casualcms.service.handlers, categories=["messagebus"])


async def bootstrap(settings: dict[str, Any]) -> FastAPI:
    with FastAPIConfigurator(settings) as configurator:
        configure(configurator)

    app = configurator.app
    return app


async def asyncmain(settings: dict[str, str] = SETTINGS) -> None:
    config = Config()
    complete_settings: dict[str, str] = settings
    if settings is not SETTINGS:
        complete_settings = SETTINGS.copy()
        complete_settings.update(settings)
    config.bind = complete_settings["server_host"].split(",")
    app = await bootstrap(complete_settings)
    await serve(app, config)  # type: ignore

def main(settings: dict[str, str] = SETTINGS):
    asyncio.run(asyncmain(settings))

if __name__ == "__main__":
    main()
