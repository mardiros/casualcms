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

        host = request.url.hostname or ""
        if request.url.scheme == "http" and request.url.port != 80:
            host += f":{request.url.port}"
        elif request.url.scheme == "https" and request.url.port != 443:
            host += f":{request.url.port}"
        site = await uow.sites.by_hostname(host)
        if site.is_err():
            raise HTTPException(
                status_code=404,
                detail=[{"msg": f"Host {request.url.hostname} not found"}],
            )
        site_ok = site.unwrap()
        if site_ok.secure and request.url.scheme == "http":
            return Response(
                status_code=302,
                headers={"location": f"https://{host}/{request.url.path}"},
            )

        root_page_path = site.unwrap().root_page_path
        page = await uow.pages.by_path(f"{root_page_path}/{path}".rstrip("/"))
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
