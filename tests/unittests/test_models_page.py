from pydantic import Field

from casualcms.domain.model import Page


class MyPage(Page):
    body: str = Field(...)

    class Meta:
        template = "page.jinja2"


class MyPage2(MyPage):
    footer: str = Field(...)


def test_page_metadata():

    page = MyPage(id="a", slug="", title="awesome", description="", body="Hello!")
    assert page.get_template() == "page.jinja2"
    assert page.get_context() == {
        "id": "a",
        "slug": "",
        "title": "awesome",
        "description": "",
        "body": "Hello!",
    }

    page2 = MyPage2(
        id="a", slug="", title="awesome", description="", body="Hello!", footer="Bye"
    )
    assert page2.get_template() == "page.jinja2"


def test_page_tree():
    page = Page(id="a", slug="", title="awesome", description="")

    assert page.path == "/"

    page2 = Page(id="b", slug="sub", title="sub", description="", parent=page)
    assert page2.path == "/sub"

    page3 = Page(id="b", slug="sum", title="sum", description="", parent=page2)
    assert page3.path == "/sub/sum"
