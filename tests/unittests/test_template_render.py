from pathlib import Path

from casualcms.adapters.jinja2 import Jinja2TemplateRender, build_searchpath
from casualcms.config import Settings
from casualcms.domain.model.snippet import Snippet
from casualcms.service.unit_of_work import AbstractUnitOfWork


def test_build_searchpath():
    path_list = build_searchpath("casualcms:templates,/tmp")
    path = str(
        (
            Path(__file__).parent.parent.parent / "src" / "casualcms" / "templates"
        ).resolve()
    )

    assert path_list == [path, "/tmp"]


async def test_render_template(uow: AbstractUnitOfWork, app_settings: Settings):
    renderer = Jinja2TemplateRender(uow, app_settings.template_search_path)
    data = await renderer.render_template("test.jinja2", {"title": "hey"})
    assert data == "<html><title>hey</title></html>"


async def test_render_template_with_snippet(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet,
):
    renderer = Jinja2TemplateRender(uow, app_settings.template_search_path)
    data = await renderer.render_template("test_with_snippet.jinja2", {})
    assert (
        data
        == """
        <html>
<h1>A personal blog</h1>
<ul role="nav"><li><a href="/cats">cats</a></li><li><a href="/dogs">dogs</a></li></ul>
</html>
    """.strip()
    )
