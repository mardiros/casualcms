from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from .base import router
from . import authntoken


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    app.include_router(router, prefix="/api")
