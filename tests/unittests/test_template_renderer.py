from pathlib import Path

from result import Err, Ok

from casualcms.adapters.jinja2 import Jinja2TemplateRender, build_searchpath
from casualcms.config import Settings
from casualcms.domain.model.setting import Setting
from casualcms.domain.model.site import Site
from casualcms.domain.model.snippet import Snippet
from casualcms.domain.repositories.setting import SettingRepositoryError
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
    renderer = Jinja2TemplateRender(uow, app_settings.template_search_path, "")
    data = await renderer.render_template("test.jinja2", {"page": {"title": "hey"}})
    assert data == "<html><title>hey</title></html>"


async def test_render_template_with_snippet(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet,
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(uow, app_settings.template_search_path, "")
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


async def test_get_setting(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet,
    default_site: Site,
    contact_setting: Setting,
    ff_setting: Setting,
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        assert await renderer.get_setting("foo.bar") == ""
        assert renderer._settings == {  # type: ignore
            "foo": Err(SettingRepositoryError.setting_not_found),
        }
        assert await renderer.get_setting("contact") == contact_setting
        assert renderer._settings == {  # type: ignore
            "foo": Err(SettingRepositoryError.setting_not_found),
            "contact": Ok(contact_setting),
        }
        assert await renderer.get_setting("contact.email") == "email@example.net"
        assert await renderer.get_setting("ff.use_stuff") is True

    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        # Cache is empty
        assert renderer._settings == {}  # type: ignore


async def test_render_template_with_snippet_and_setting(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet,
    default_site: Site,
    contact_setting: Setting,
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
    data = await renderer.render_template("test_with_snippet.jinja2", {})
    nav = "".join(
        [
            '<li><a href="/cats">cats</a></li>',
            '<li><a href="/dogs">dogs</a></li>',
            '<li><a href="mailto:email@example.net">Contact Us</a></li>',
        ]
    )

    assert (
        data
        == f"""
        <html>
<h1>A personal blog</h1>
<ul role="nav">{nav}</ul>
</html>
    """.strip()
    )
