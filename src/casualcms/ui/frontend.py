from fastapi import HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles

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
        hostname = request.url.hostname or ""
        if request.url.port:
            hostname += f":{request.url.port}"
        rsite = await uow.sites.by_hostname(hostname)
        if rsite.is_err():
            # Implement Default site here
            raise HTTPException(
                status_code=404,
                detail=[{"msg": f"Host {request.url.hostname} not found"}],
            )
        else:
            site = rsite.unwrap()
            if site.secure and request.url.scheme == "http":
                return Response(
                    status_code=302,
                    headers={"location": f"https://{hostname}/{request.url.path}"},
                )

        rpage = await uow.pages.by_url(f"//{hostname}/{request.url.path}".rstrip("/"))
        # page = await uow.drafts.by_path(f"{root_page_path}/{path}".rstrip("/"))
        if rpage.is_err():
            raise HTTPException(
                status_code=404,
                detail=[{"msg": f"Page {path} not found"}],
            )
        page = rpage.unwrap()
        renderer = Jinja2TemplateRender(
            uow, app.settings.template_search_path, hostname
        )
        data = await renderer.render_template(page.template, page.body)
        await uow.rollback()
    return Response(data)


@configure
def includeme(app: FastAPIConfigurator) -> None:
    assets = app.config.settings.assets_path
    if assets:
        app.mount(
            "/assets",
            StaticFiles(directory=app.config.settings.assets_path),
            name="assets",
        )
    app.add_api_route("/{path:path}", serve_pages, methods=["GET"])
