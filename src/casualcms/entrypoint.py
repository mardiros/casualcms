from typing import Any

import casualcms.api
import casualcms.ui
import casualcms.service.handlers
from casualcms.adapters.fastapi import FastAPIConfigurator

settings: dict[str, Any] = {
    "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
}

def configure(configurator: FastAPIConfigurator):
    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    configurator.scan(casualcms.ui, categories=["fastapi"])

    # configure message bus
    configurator.scan(casualcms.service.handlers, categories=["messagebus"])


with FastAPIConfigurator(settings) as configurator:
    configure(configurator)


    app = configurator.app
