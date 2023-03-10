from pathlib import Path

from fastapi import Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Receive, Scope, Send

from casualcms.adapters.fastapi import FastAPIConfigurator, configure

admin_ui_dir = Path(__file__).parent / "webapp_compiled"
template_dir = Path(__file__).parent / "templates"
favicon_path = Path(__file__).parent / "favicon.ico"


react_app = StaticFiles(directory=str(admin_ui_dir.resolve()), html=True)


async def favicon() -> Response:
    return FileResponse(favicon_path)


async def serve_admin_ui(scope: Scope, receive: Receive, send: Send) -> None:
    """
    Serve the react app and its static assets.

    Routes in the react app cannot contains `.`.
    """
    if "." not in scope["path"]:
        scope["path"] = "index.html"
    await react_app(scope, receive, send)


@configure
def includeme(app: FastAPIConfigurator) -> None:
    app.add_api_route("/favicon.ico", favicon, methods=["GET"])
    app.mount("/admin", serve_admin_ui, name="backoffice")
