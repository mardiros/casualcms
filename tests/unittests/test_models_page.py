from typing import Any, Dict

import pytest

from casualcms.domain.model import AbstractPageError, get_available_subtypes
from casualcms.domain.model.draft import resolve_page_type

from ..casualblog.models import (
    AbstractPage,
    BlogPage,
    CategoryPage,
    HomePage,
    SectionPage,
)


def test_page_metadata():
    page = HomePage(
        id="a",
        slug="home",
        title="awesome",
        description="",
        hero_title="You are awesome",
        body=[{"body": "Hello!"}],
    )
    assert page.get_template() == "homepage.jinja2"
    assert page.__meta__.abstract is False
    assert page.__meta__.type == "blog:HomePage"


def test_page_abstract_raise():
    with pytest.raises(AbstractPageError) as context:
        AbstractPage(
            id="a",
            slug="home",
            title="awesome",
            description="",
            hero_title="You are awesome",
        )
    assert str(context.value) == "Page AbstractPage is abstract"


def test_page_tree():
    page = HomePage(
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

    assert pages == {HomePage}

    pages = get_available_subtypes(HomePage)
    assert pages == {CategoryPage, SectionPage}


@pytest.mark.parametrize(
    "params",
    [
        {"name": "blog:HomePage", "class": HomePage},
        {"name": "blog:SectionPage", "class": SectionPage},
    ],
)
def test_resolve_page_type(params: Dict[str, Any]):
    page = resolve_page_type(params["name"]).unwrap()
    assert page is params["class"]


def test_resolve_page_type_error():
    err = resolve_page_type("blog:sectionpage").unwrap_err()
    assert err.name == "unregistered"
