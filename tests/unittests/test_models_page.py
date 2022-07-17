from typing import Any, Dict

import pytest

from casualcms.domain.model import AbstractPageError, get_available_subtypes
from casualcms.domain.model.page import UnregisterType, resolve_type

from .fixtures import AbstractPage, BlogPage, CategoryPage, RootPage, SectionPage


def test_page_metadata():
    page = RootPage(
        id="a",
        slug="",
        title="awesome",
        description="",
        hero_title="You are awesome",
        body=[{"body": "Hello!"}],
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
            body=[{"body": "Hello!"}],
        )
    assert str(context.value) == "Page AbstractPage is abstract"


def test_page_tree():
    page = RootPage(
        id="a",
        slug="index",
        title="awesome",
        hero_title="awesome",
        description="",
        body=[{"body": "Hello!"}],
    )
    assert page.path == "/index"

    page2 = CategoryPage(
        id="b",
        slug="sub",
        title="sub",
        description="",
        hero_title="awesome",
        parent=page,
        body=[{"body": "Hello!"}],
    )
    assert page2.path == "/index/sub"

    page3 = BlogPage(
        id="b",
        slug="sum",
        title="sum",
        description="",
        hero_title="awesome",
        parent=page2,
        body=[{"body": "Hello!"}],
    )
    assert page3.path == "/index/sub/sum"


def test_page_types():
    pages = get_available_subtypes(None)
    from tests.functionals.casualblog.models import HomePage  # FIXME shoud not leak

    assert pages == {HomePage, RootPage}

    pages = get_available_subtypes(RootPage)
    assert pages == {CategoryPage, SectionPage}


@pytest.mark.parametrize(
    "params",
    [
        {"name": "tests.unittests.fixtures:RootPage", "class": RootPage},
        {"name": "casual:SectionPage", "class": SectionPage},
    ],
)
def test_resolve_type(params: Dict[str, Any]):
    page = resolve_type(params["name"])
    assert page is params["class"]


def test_resolve_type_error():
    with pytest.raises(UnregisterType) as ctx:
        resolve_type("casual:sectionpage")
    assert str(ctx.value) == "Unregistered type casual:sectionpage"
