from pathlib import Path

from casualcms.adapters.jinja2 import Jinja2TemplateRender, build_searchpath
from casualcms.config import Settings


def test_build_searchpath():
    path_list = build_searchpath("casualcms:templates,/tmp")
    path = str(
        (
            Path(__file__).parent.parent.parent / "src" / "casualcms" / "templates"
        ).resolve()
    )

    assert path_list == [path, "/tmp"]


def test_render_template(app_settings: Settings):
    renderer = Jinja2TemplateRender(app_settings.template_search_path)
    data = renderer.render_template("page.jinja2", {"title": "hey"})
    assert data == "<html><title>hey</title></html>"
