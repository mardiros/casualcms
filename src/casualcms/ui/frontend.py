from fastapi import HTTPException, Request, Response

from casualcms.adapters.fastapi import AppConfig, FastAPIConfigurator, configure
from casualcms.adapters.jinja2 import Jinja2TemplateRender


async def serve_pages(
    path: str,
    request: Request,
    app: AppConfig = FastAPIConfigurator.depends,
) -> Response:
    path = path.strip("/") or "/"
    async with app.uow as uow:
        if path == "admin":
            raise HTTPException(
                status_code=302,
                headers={"location": "/admin/"},
            )

        site = await uow.sites.by_hostname(request.url.hostname)

        page = await uow.pages.by_path(f"/{path}")
        if page.is_err():
            raise HTTPException(
                status_code=404,
                detail=[{"msg": f"Page {path} not found"}],
            )
        await uow.commit()
    rpage = page.unwrap()
    renderer = Jinja2TemplateRender(app.settings.template_search_path)
    data = renderer.render_template(
        rpage.get_template(),
        rpage.get_context(),
    )
    return Response(data)


@configure
def includeme(app: FastAPIConfigurator) -> None:
    app.add_api_route("/{path:path}", serve_pages, methods=["GET"])
