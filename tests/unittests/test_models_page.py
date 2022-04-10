import pytest

from casualcms.domain.model import AbstractPageError, get_available_subtypes

from .fixtures import AbstractPage, BlogPage, CategoryPage, RootPage, SectionPage


def test_page_metadata():
    page = RootPage(
        id="a",
        slug="",
        title="awesome",
        description="",
        hero_title="You are awesome",
        body="Hello!",
    )
    assert page.get_template() == "page.jinja2"
    assert page.__meta__.abstract is False
    assert page.__meta__.type == "tests.unittests.fixtures:RootPage"


def test_page_abstract_raise():
    with pytest.raises(AbstractPageError) as context:
        AbstractPage(
            id="a",
            slug="",
            title="awesome",
            description="",
            hero_title="You are awesome",
            body="Hello!",
        )
    assert str(context.value) == "Page AbstractPage is abstract"


def test_page_tree():
    page = RootPage(
        id="a",
        slug="",
        title="awesome",
        hero_title="awesome",
        description="",
        body="Hello!",
    )
    assert page.path == "/"

    page2 = CategoryPage(
        id="b",
        slug="sub",
        title="sub",
        description="",
        hero_title="awesome",
        parent=page,
        body="Hello!",
    )
    assert page2.path == "/sub"

    page3 = BlogPage(
        id="b",
        slug="sum",
        title="sum",
        description="",
        hero_title="awesome",
        parent=page2,
        body="Hello!",
    )
    assert page3.path == "/sub/sum"


def test_page_types():
    pages = get_available_subtypes(None)
    assert pages == {RootPage}

    pages = get_available_subtypes(RootPage)
    assert pages == {CategoryPage, SectionPage}
