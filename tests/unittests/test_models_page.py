from typing import Any

from pydantic import Field

from casualcms.domain.model import Page


def test_page_metadata(app_settings: Any):
    class MyPage(Page):
        body: str = Field(...)

        class Config:
            template = "page.jinja2"

    page = MyPage(id="a", slug="abc", title="awesome", description="", body="Hello!")
    assert page.__config__.template == "page.jinja2"
    assert page.get_context() == {
        "id": "a",
        "slug": "abc",
        "title": "awesome",
        "description": "",
        "body": "Hello!",
    }
