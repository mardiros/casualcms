from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from . import authntoken
from .base import router


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    app.include_router(router, prefix="/api")
