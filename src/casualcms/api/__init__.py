from casualcms.adapters.fastapi import FastAPIConfigurator, configure

from . import (
    authntoken,
    draft,
    page_type,
    setting,
    setting_type,
    site,
    snippet,
    snippet_type,
)
from .base import router


@configure
def includeme(app: FastAPIConfigurator) -> None:
    router.add_api_route("/authntokens", authntoken.authenticate, methods=["POST"])
    router.add_api_route(
        "/authntokens",
        authntoken.logout,
        methods=["DELETE"],
    )
    router.add_api_route(
        "/drafts", draft.create_draft, methods=["POST"], status_code=201
    )
    router.add_api_route("/drafts", draft.list_drafts, methods=["GET"])
    router.add_api_route("/drafts/{path:path}", draft.show_draft, methods=["GET"])
    router.add_api_route(
        "/drafts/{path:path}", draft.update_draft, methods=["PATCH"], status_code=202
    )
    router.add_api_route(
        "/drafts/{path:path}", draft.delete_draft, methods=["DELETE"], status_code=204
    )
    router.add_api_route("/pages-types", page_type.list_templates, methods=["GET"])
    router.add_api_route(
        "/pages-types/{type}", page_type.show_template, methods=["GET"]
    )

    router.add_api_route("/sites", site.create_site, methods=["POST"], status_code=201)
    router.add_api_route("/sites", site.list_sites, methods=["GET"])
    router.add_api_route("/sites/{hostname}", site.show_site, methods=["GET"])
    router.add_api_route(
        "/sites/{current_hostname}",
        site.update_site,
        methods=["PATCH"],
        status_code=202,
    )
    router.add_api_route(
        "/sites/{hostname}", site.delete_site, methods=["DELETE"], status_code=204
    )

    router.add_api_route(
        "/snippets", snippet.create_snippet, methods=["POST"], status_code=201
    )
    router.add_api_route("/snippets", snippet.list_snippets, methods=["GET"])
    router.add_api_route("/snippets/{slug}", snippet.show_snippet, methods=["GET"])
    router.add_api_route(
        "/snippets/{slug}", snippet.delete_snippet, methods=["DELETE"], status_code=204
    )
    router.add_api_route(
        "/snippets/{slug}", snippet.update_snippet, methods=["PATCH"], status_code=202
    )
    router.add_api_route("/snippets-types", snippet_type.list_types, methods=["GET"])
    router.add_api_route(
        "/snippets-types/{type}", snippet_type.show_type, methods=["GET"]
    )

    router.add_api_route(
        "/settings/{hostname}",
        setting.create_setting,
        methods=["POST"],
        status_code=201,
    )
    router.add_api_route("/settings/{hostname}", setting.list_settings, methods=["GET"])
    router.add_api_route(
        "/settings/{hostname}/{key}", setting.show_setting, methods=["GET"]
    )
    router.add_api_route(
        "/settings/{hostname}/{key}",
        setting.delete_setting,
        methods=["DELETE"],
        status_code=204,
    )
    router.add_api_route(
        "/settings/{hostname}/{key}",
        setting.update_setting,
        methods=["PATCH"],
        status_code=202,
    )
    router.add_api_route("/settings-types", setting_type.list_types, methods=["GET"])
    router.add_api_route(
        "/settings-types/{key}", setting_type.show_type, methods=["GET"]
    )

    app.include_router(router, prefix="/api")
