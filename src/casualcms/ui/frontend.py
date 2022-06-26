from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator, configure
from fastapi import HTTPException, Response

from casualcms.adapters.jinja2 import Jinja2TemplateRender


async def serve_pages(
    path: str,
    app: AppConfig = FastAPIConfigurator.depends,
) -> Response:
    async with app.uow as uow:
        page = await uow.pages.by_path(path or "/")
        if page.is_err():
            raise HTTPException(
                status_code=404,
                detail=[{"msg": "Page not found"}],
            )
    page = page.unwrap()
    renderer = Jinja2TemplateRender(app.settings.template_search_path)
    data = renderer.render_template(
        page.get_template(),
        page.get_context(),
    )
    return Response(data)


@configure
def includeme(app: FastAPIConfigurator) -> None:
    app.add_api_route("/{path:path}", serve_pages, methods=["GET"])
