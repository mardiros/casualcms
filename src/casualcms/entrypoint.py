from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Receive, Scope, Send

admin_ui_dir = Path(__file__).parent / "admin"
template_dir = Path(__file__).parent / "templates"
favicon_path = Path(__file__).parent / "favicon.ico"


app = FastAPI()

react_app = StaticFiles(directory=str(admin_ui_dir.resolve()), html=True)


@app.get("/favicon.ico")
async def favicon() -> Response:
    return FileResponse(favicon_path)


async def serve_admin_ui(scope: Scope, receive: Receive, send: Send):
    """
    Serve the react app and its static assets.

    Routes in the react app cannot contains `.`.
    """
    if "." not in scope["path"]:
        scope["path"] = "index.html"
    resp = await react_app(scope, receive, send)
    return resp


app.mount("/admin", serve_admin_ui, name="ui")
