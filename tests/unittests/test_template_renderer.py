import textwrap
from pathlib import Path
from typing import Any

from result import Err, Ok

from casualcms.adapters.jinja2 import Jinja2TemplateRender, build_searchpath
from casualcms.config import Settings
from casualcms.domain.model import DraftPage, Setting, Site, Snippet
from casualcms.domain.repositories.setting import SettingRepositoryError
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.casualblog.models import (
    CodeBlock,
    ContactSetting,
    FeatureFlagSetting,
    HeaderSnippet,
    HomePage,
    ParagraphBlock,
    SectionPage,
    SnippetBlockPage,
)
from .long_text import EXPECTED_CODEBLOCK


def test_build_searchpath():
    path_list = build_searchpath("casualcms:templates,/tmp")
    path = str(
        (
            Path(__file__).parent.parent.parent / "src" / "casualcms" / "templates"
        ).resolve()
    )

    assert path_list == [path, "/tmp"]


async def test_render_page(
    uow: AbstractUnitOfWork, draft_hp: DraftPage[HomePage], app_settings: Settings
):
    renderer = Jinja2TemplateRender(uow, app_settings.template_search_path, "")
    data = await renderer.render_page(draft_hp.page)
    assert """<h2>Welcome aboard!</h2>""" in data


async def test_render_template_with_snippet(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    draft_hp: DraftPage[HomePage],
    header_snippet: Snippet[HeaderSnippet],
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(uow, app_settings.template_search_path, "")
    data = await renderer.render_snippet(header_snippet.snippet, draft_hp.page)
    assert (
        data
        == """
<h1>A personal blog</h1>
<ul role="nav"><li><a href="/cats">cats</a></li><li><a href="/dogs">dogs</a></li></ul>
    """.strip()
    )


async def test_get_setting(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet[HeaderSnippet],
    default_site: Site,
    contact_setting: Setting[ContactSetting],
    ff_setting: Setting[FeatureFlagSetting],
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        assert await renderer.get_setting("foo.bar") == ""
        assert renderer._settings == {  # type: ignore
            "foo": Err(SettingRepositoryError.setting_not_found),
        }
        assert await renderer.get_setting("contact") == contact_setting.setting
        assert renderer._settings == {  # type: ignore
            "foo": Err(SettingRepositoryError.setting_not_found),
            "contact": Ok(contact_setting),
        }
        assert await renderer.get_setting("contact.email") == "email@example.net"
        assert (
            await renderer.get_setting("ff.use_stuff") is ff_setting.setting.use_stuff
        )

    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        # Cache is empty
        assert renderer._settings == {}  # type: ignore


async def test_render_template_with_snippet_and_setting(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    header_snippet: Snippet[HeaderSnippet],
    draft_hp: DraftPage[HomePage],
    default_site: Site,
    contact_setting: Setting[Any],
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        data = await renderer.render_snippet(
            header_snippet.snippet,
            draft_hp.page,
        )
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
<h1>A personal blog</h1>
<ul role="nav">{nav}</ul>
    """.strip()
    )


async def test_render_template_with_block(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    draft_hp: DraftPage[HomePage],
    default_site: Site,
    section_page: DraftPage[SectionPage],
):

    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        data = await renderer.render_block(
            section_page.page.box,
            section_page.page,
        )
    assert (
        data.strip()
        == textwrap.dedent(
            """\
            <div>
              <h4>a box</h4>
              <p>lorem ipsum</p>
            </div>
            """
        ).strip()
    )


async def test_render_template_with_generic_block(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    default_site: Site,
    generic_section_page: DraftPage[SectionPage],
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        data = await renderer.render_page(generic_section_page.page)
    assert (
        data.strip()
        == textwrap.dedent(
            """\
            <body><dl><dt>a box</dt>
                <dd><div>lorem ipsum</div></dd><dt>another box</dt>
                <dd><div>lorem atchoum</div></dd></dl></body>
            """
        ).strip()
    )


async def test_render_page_with_snippet_and_block(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    draft_hp: DraftPage[HomePage],
    default_site: Site,
    snippet_block_page: DraftPage[SnippetBlockPage],
):
    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        data = await renderer.render_page(snippet_block_page.page)
    assert (
        data.strip()
        == textwrap.dedent(
            """\
            <div class="page">
              <div class="snippet">
              <h4>page / snippet title / box title</h4>
            </div>
            </div>
            """
        ).strip()
    )


async def test_render_template_with_many_blocks(
    uow: AbstractUnitOfWork,
    app_settings: Settings,
    draft_hp: DraftPage[HomePage],
    default_site: Site,
):
    draft_hp.page.body = [
        ParagraphBlock(title="Ici un truc", body="bla bla"),
        CodeBlock(language="Python", code="""async def main():\n    ...\n"""),
        ParagraphBlock(title="Other", body="stuff"),
        CodeBlock(language="Python", code="""def main():\n    ...\n"""),
    ]
    ...

    async with uow as uow:
        renderer = Jinja2TemplateRender(
            uow, app_settings.template_search_path, default_site.hostname
        )
        data = await renderer.render_page(draft_hp.page)
    assert data.strip() == EXPECTED_CODEBLOCK
