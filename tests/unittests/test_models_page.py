from typing import Any

from casualcms.domain.model import Page


def test_page_metadata(app_settings: Any):
    class MyPage(Page):
        class Config:
            template = "page.jinja2"

    page = MyPage(id="a", slug="a", title="awesome")
    assert page.__config__.template == "page.jinja2"
    assert page.render() == f"<html><title>{page.title}</title></html>"
