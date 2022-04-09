from pydantic import Field

from casualcms.domain.model import Page


def test_page_metadata():
    class MyPage(Page):
        body: str = Field(...)

        class Config:
            template = "page.jinja2"

    page = MyPage(id="a", slug="", title="awesome", description="", body="Hello!")
    assert page.__config__.template == "page.jinja2"
    assert page.get_context() == {
        "id": "a",
        "slug": "",
        "title": "awesome",
        "description": "",
        "body": "Hello!",
        "parent": None,
    }


def test_page_tree():
    page = Page(id="a", slug="", title="awesome", description="")

    assert page.path == "/"

    page2 = Page(id="b", slug="sub", title="sub", description="", parent=page)
    assert page2.path == "/sub"

    page3 = Page(id="b", slug="sum", title="sum", description="", parent=page2)
    assert page3.path == "/sub/sum"
