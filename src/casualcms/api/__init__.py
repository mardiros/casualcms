from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from . import authntoken, page
from .base import router


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    router.add_api_route("/pages", page.create_page, methods=["POST"])
    app.include_router(router, prefix="/api")
