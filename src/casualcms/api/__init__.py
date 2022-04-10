from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from . import authntoken, page, template
from .base import router


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    router.add_api_route("/pages", page.create_page, methods=["POST"])
    router.add_api_route("/templates", template.list_templates, methods=["GET"])
    app.include_router(router, prefix="/api")
