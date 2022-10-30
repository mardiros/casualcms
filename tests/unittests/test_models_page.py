from typing import Any, Dict, Mapping

import pytest

from casualcms.domain.model import (
    AbstractPageError,
    get_available_subtypes,
    resolve_page_type,
)
from casualcms.domain.model.abstract_page import AbstractPage, PublicMetadata
from casualcms.domain.model.breadcrumb import Breadcrumb, BreadcrumbItem
from casualcms.domain.model.site import Site

from ..casualblog.models import BasePage, BlogPage, CategoryPage, HomePage, SectionPage

site = Site(
    id="xxx",
    hostname="www",
    root_page_path="/index",
    default=False,
    secure=True,
    draft_id=None,  # handled by the repository
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
    assert page.__meta__.template == "homepage.jinja2"
    assert page.__meta__.abstract is False
    assert page.__meta__.type == "blog:HomePage"


def test_page_abstract_raise():
    with pytest.raises(AbstractPageError) as context:
        BasePage(
            hero_title="You are awesome",
        )
    assert str(context.value) == "Page BasePage is abstract"


@pytest.mark.parametrize(
    "page_type,expected",
    [
        (
            HomePage,
            {
                "body": {
                    "items": {
                        "body": {
                            "ui:placeholder": "body",
                            "ui:widget": "richtext",
                            "ui:options": {"features": ["bold", "italic", "h5"]},
                        },
                        "title": {"ui:placeholder": "title", "ui:widget": "text"},
                    }
                },
                "description": {"ui:placeholder": "description", "ui:widget": "text"},
                "hero_title": {"ui:placeholder": "hero_title", "ui:widget": "text"},
                "slug": {"ui:placeholder": "slug", "ui:widget": "text"},
                "title": {"ui:placeholder": "title", "ui:widget": "text"},
            },
        ),
        (
            SectionPage,
            {
                "box": {
                    "paragraph": {
                        "ui:placeholder": "paragraph",
                        "ui:widget": "textarea",
                    },
                    "title": {"ui:placeholder": "title", "ui:widget": "text"},
                },
                "boxes": {
                    "items": {
                        "items": {
                            "paragraph": {
                                "ui:placeholder": "paragraph",
                                "ui:widget": "textarea",
                            },
                            "title": {"ui:placeholder": "title", "ui:widget": "text"},
                        }
                    }
                },
                "description": {"ui:placeholder": "description", "ui:widget": "text"},
                "hero_title": {"ui:placeholder": "hero_title", "ui:widget": "text"},
                "intro": {
                    "body": {
                        "ui:placeholder": "body",
                        "ui:widget": "richtext",
                        "ui:options": {"features": ["bold", "italic", "h5"]},
                    },
                    "title": {"ui:placeholder": "title", "ui:widget": "text"},
                },
                "slug": {"ui:placeholder": "slug", "ui:widget": "text"},
                "title": {"ui:placeholder": "title", "ui:widget": "text"},
            },
        ),
    ],
)
def test_page_ui_schema(page_type: AbstractPage, expected: Mapping[str, Any]):
    assert page_type.ui_schema() == expected


@pytest.mark.parametrize(
    "params",
    [
        {"root_url": "", "expected_root_path": "/index", "site": None},
        {"root_url": "https://www/", "expected_root_path": "", "site": site},
    ],
)
def test_page_tree(params: Mapping[str, Any]):
    root_url = params["root_url"]
    expected_root_path = params["expected_root_path"]
    expected_root_breadcrumb = BreadcrumbItem(
        position=1,
        name="awesome",
        item=root_url,
        slug="index",
        path=expected_root_path,
    )
    expected_sub_breadcrumb = BreadcrumbItem(
        position=2,
        name="sub",
        item=f"{root_url}sub",
        slug="sub",
        path=f"{expected_root_path}/sub",
    )

    page = HomePage(
        id="a",
        slug="index",
        title="awesome",
        hero_title="awesome",
        description="",
        body=[{"body": "Hello!"}],
        site=params["site"],
    )
    assert page.metadata == PublicMetadata(
        breadcrumb=Breadcrumb(itemListElement=[expected_root_breadcrumb]),
        type="blog:HomePage",
        path=expected_root_path,
        canonical_url=root_url,
    )

    page2 = CategoryPage(
        id="b",
        slug="sub",
        title="sub",
        description="",
        hero_title="awesome",
        parent=page,
        body=[{"body": "Hello!"}],
        site=params["site"],
    )

    assert page2.metadata == PublicMetadata(
        breadcrumb=Breadcrumb(
            itemListElement=[
                expected_root_breadcrumb,
                expected_sub_breadcrumb,
            ]
        ),
        type="blog:CategoryPage",
        path=f"{expected_root_path}/sub",
        canonical_url=f"{root_url}sub",
    )

    page3 = BlogPage(
        id="b",
        slug="sum",
        title="En sum sum",
        description="",
        hero_title="awesome",
        parent=page2,
        body=[{"body": "Hello!"}],
        site=params["site"],
    )
    assert page3.metadata == PublicMetadata(
        breadcrumb=Breadcrumb(
            itemListElement=[
                expected_root_breadcrumb,
                expected_sub_breadcrumb,
                BreadcrumbItem(
                    position=3,
                    name="En sum sum",
                    item=f"{root_url}sub/sum",
                    path=f"{expected_root_path}/sub/sum",
                    slug="sum",
                ),
            ]
        ),
        type="blog:BlogPage",
        path=f"{expected_root_path}/sub/sum",
        canonical_url=f"{root_url}sub/sum",
    )


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
