from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from . import authntoken, page, page_template, site, snippet, snippet_type
from .base import router


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    router.add_api_route(
        "/authntokens",
        authntoken.logout,
        methods=["DELETE"],
    )
    router.add_api_route("/pages", page.create_page, methods=["POST"])
    router.add_api_route("/pages", page.list_pages, methods=["GET"])
    router.add_api_route("/pages/{path:path}", page.get_page, methods=["GET"])
    router.add_api_route("/pages/{path:path}", page.update_page, methods=["PATCH"])
    router.add_api_route("/pages/{path:path}", page.delete_page, methods=["DELETE"])

    router.add_api_route("/sites", site.create_site, methods=["POST"])
    router.add_api_route("/sites", site.list_sites, methods=["GET"])
    router.add_api_route("/sites/{hostname}", site.get_site, methods=["GET"])
    router.add_api_route("/sites/{hostname}", site.delete_site, methods=["DELETE"])

    router.add_api_route("/snippets", snippet.create_snippet, methods=["POST"])
    router.add_api_route("/snippets", snippet.list_snippets, methods=["GET"])
    router.add_api_route("/snippets-types", snippet_type.list_types, methods=["GET"])
    router.add_api_route(
        "/snippets-types/{type}", snippet_type.show_type, methods=["GET"]
    )

    router.add_api_route("/templates", page_template.list_templates, methods=["GET"])
    router.add_api_route(
        "/templates/{type}", page_template.show_template, methods=["GET"]
    )

    app.include_router(router, prefix="/api")
