from typing import Any

import casualcms.api
import casualcms.ui
from casualcms.adapters.fastapi import FastAPIConfigurator

settings: dict[str, Any] = {
    "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
}

with FastAPIConfigurator(settings) as configurator:
    # configure message bus

    # inject routes
    configurator.scan(casualcms.api, categories=["fastapi"])
    configurator.scan(casualcms.ui, categories=["fastapi"])

    # import casualcms.service.handlers
    # self.scan(casualcms.service.handlers, categories=["messagebus"])

    app = configurator.app
