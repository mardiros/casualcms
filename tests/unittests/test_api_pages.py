from typing import Any, Mapping, cast

import pytest
from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.casualblog.models import HomePage


async def test_api_create_page_unauthenticated(
    client: TestClient, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/pages",
        headers={},
        json={"type": "blog:HomePage", "payload": {}},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_create_page(
    client: TestClient, authntoken: AuthnToken, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/pages",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "type": "blog:HomePage",
            "payload": {
                "id": "abc",
                "slug": "index",
                "title": "Root Page",
                "description": "The home page",
                "hero_title": "You are awesome",
                "body": [{"body": "lorem ipsum"}],
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"href": "/index"}
    async with uow as uow:
        page = (await uow.pages.by_path("/index")).unwrap()
        assert page.dict() == {
            "id": "abc",
            "slug": "index",
            "title": "Root Page",
            "description": "The home page",
            "hero_title": "You are awesome",
            "body": [{"title": None, "body": "lorem ipsum"}],
        }


async def test_api_list_root_page(
    client: TestClient, authntoken: AuthnToken, home_page: Page
):
    resp = client.get(
        "/api/pages",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "slug": home_page.slug,
            "title": home_page.title,
            "meta": {
                "path": home_page.path,
                "type": home_page.__meta__.type,
            },
        }
    ]


async def test_create_subpage(
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
    uow: AbstractUnitOfWork,
):
    resp = client.post(
        "/api/pages",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "type": "blog:CategoryPage",
            "parent": "/home",
            "payload": {
                "id": "abcd",
                "slug": "test",
                "title": "sub Page",
                "description": "A sub page",
                "hero_title": "A sub page",
            },
        },
    )
    assert resp.json() == {"href": "/home/test"}
    assert resp.status_code == 200
    async with uow as uow:
        page = (await uow.pages.by_path("/home/test")).unwrap()
        assert page.dict() == {
            "id": "abcd",
            "slug": "test",
            "title": "sub Page",
            "description": "A sub page",
            "hero_title": "A sub page",
            "intro": None,
        }

    async with uow as uow:
        pages = (await uow.pages.by_parent("/home")).unwrap()
        pages_dict = [page.dict() for page in pages]
        assert pages_dict == [
            {
                "id": "abcd",
                "slug": "test",
                "title": "sub Page",
                "description": "A sub page",
                "hero_title": "A sub page",
                "intro": None,
            }
        ]


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/api/pages/home",
            "response": {
                "meta": {
                    "type": "blog:HomePage",
                    "path": "/home",
                },
                "slug": "home",
                "title": "hello world - casualcms",
                "description": "I am so glad to be there",
                "hero_title": "Welcome aboard!",
                "body": [],
            },
        },
        {
            "path": "/api/pages/home/sub",
            "response": {
                "meta": {
                    "type": "blog:CategoryPage",
                    "path": "/home/sub",
                },
                "slug": "sub",
                "title": "a sub page",
                "description": "I am so glad to be a sub page",
                "hero_title": "a sub page",
                "intro": None,
            },
        },
    ],
)
async def test_get_page(
    params: Mapping[str, Any],
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
    sub_page: Page,
    uow: AbstractUnitOfWork,
):
    resp = client.get(
        params["path"],
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    params["response"]["id"] = (
        home_page.id if params["response"]["slug"] == "home" else sub_page.id
    )
    assert resp.json() == params["response"]


async def test_update_home_page_content(
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
    uow: AbstractUnitOfWork,
):
    payload = {
        "slug": "new-home",
        "title": "new title",
        "description": "new description",
        "hero_title": "New hero title",
        "body": [{"body": "my new body"}],
    }
    resp = client.patch(
        f"/api/pages/{home_page.path}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=payload,
    )
    assert resp.json() == {
        "id": home_page.id,
        "meta": {
            "path": "/new-home",
            "type": "blog:HomePage",
        },
        "slug": "new-home",
        "title": "new title",
        "body": [{"body": "my new body"}],
        "description": "new description",
        "hero_title": "New hero title",
    }
    async with uow as uow:
        saved_home = cast(
            HomePage,
            (await uow.pages.by_path("/new-home")).unwrap(),
        )
    assert saved_home.slug == "new-home"
    assert saved_home.title == payload["title"]
    assert saved_home.description == payload["description"]
    assert saved_home.hero_title == payload["hero_title"]
    assert saved_home.body == payload["body"]


async def test_update_sub_page_content(
    client: TestClient,
    authntoken: AuthnToken,
    sub_page: Page,
    uow: AbstractUnitOfWork,
):
    payload = {
        "slug": "new-slug",
        "title": "new title",
    }
    resp = client.patch(
        f"/api/pages/{sub_page.path}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=payload,
    )
    assert resp.json() == {
        "id": sub_page.id,
        "meta": {
            "path": "/home/new-slug",
            "type": "blog:CategoryPage",
        },
        "slug": "new-slug",
        "title": "new title",
        "description": "I am so glad to be a sub page",
        "hero_title": "a sub page",
        "intro": None,
    }
    async with uow as uow:
        saved_home = cast(
            HomePage,
            (await uow.pages.by_path("/home/new-slug")).unwrap(),
        )
    assert saved_home.slug == "new-slug"
    assert saved_home.title == payload["title"]
