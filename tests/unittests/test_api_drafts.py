from typing import Any, Mapping, Sequence, cast

import pytest
from fastapi.testclient import TestClient

from casualcms.domain.model import AuthnToken, DraftPage
from casualcms.domain.repositories.draft import DraftRepositoryResult
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.casualblog.models import CategoryPage, HomePage


async def test_api_create_draft_unauthenticated(
    client: TestClient, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/drafts",
        headers={},
        json={"type": "blog:HomePage", "payload": {}},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_create_draft(
    client: TestClient, authntoken: AuthnToken, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/drafts",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "type": "blog:HomePage",
            "payload": {
                "slug": "index",
                "title": "Root Page",
                "description": "The home page",
                "hero_title": "You are awesome",
                "body": [{"body": "lorem ipsum"}],
            },
        },
    )
    assert resp.status_code == 201
    assert resp.json() == {"message": "Resource Created"}
    async with uow as uow:
        page: DraftPage[Any] = (await uow.drafts.by_path("/index")).unwrap()
        assert page.page.dict() == {
            "slug": "index",
            "title": "Root Page",
            "description": "The home page",
            "hero_title": "You are awesome",
            "body": [{"title": None, "body": "lorem ipsum"}],
        }


@pytest.mark.parametrize(
    "params",
    [
        {
            "request": {
                "type": "blog:HomePage",
                "payload": {
                    "title": 42,
                    "description": "The home page",
                    "hero_title": "You are awesome",
                    "body": [{"body": True}],
                },
            },
            "expected_response": {
                "detail": [
                    {
                        "loc": ["body", "payload"],
                        "msg": "Missing slug",
                        "type": "value_error",
                    }
                ],
            },
        },
        {
            "request": {
                "type": "blog:UnknownPage",
                "payload": {
                    "slug": "homelander",
                    "title": 42,
                    "description": "The home page",
                    "hero_title": "You are awesome",
                    "body": [{"body": True}],
                },
            },
            "expected_response": {
                "detail": [{"loc": ["body", "type"], "msg": "Unregistered type"}]
            },
        },
        {
            "request": {
                "type": "blog:HomePage",
                "payload": {
                    "slug": "/homelander",
                    "title": 42,
                    "description": "The home page",
                    "hero_title": "You are awesome",
                    "body": [],
                },
            },
            "expected_response": {
                "detail": [
                    {
                        "loc": ["body", "payload"],
                        "msg": "Invalid slug field",
                        "type": "value_error",
                    }
                ],
            },
        },
    ],
)
async def test_api_create_draft_invalid_data_422(
    params: Mapping[str, Any],
    client: TestClient,
    authntoken: AuthnToken,
    uow: AbstractUnitOfWork,
):
    resp = client.post(
        "/api/drafts",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=params["request"],
    )
    assert resp.status_code == 422
    assert resp.json() == params["expected_response"]


async def test_api_list_draft_403(client: TestClient, draft_hp: DraftPage[HomePage]):
    resp = client.get("/api/drafts")
    assert resp.status_code == 403


async def test_api_list_root_draft_pages(
    client: TestClient, authntoken: AuthnToken, draft_hp: DraftPage[HomePage]
):
    resp = client.get(
        "/api/drafts",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "slug": draft_hp.slug,
            "title": draft_hp.title,
            "metadata": {
                "path": draft_hp.path,
                "type": draft_hp.page.__meta__.type,
                "title": draft_hp.page.__meta__.title,
            },
        }
    ]


async def test_create_draft_subpages(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.post(
        "/api/drafts",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "type": "blog:CategoryPage",
            "parent": "/home",
            "payload": {
                "slug": "test",
                "title": "sub Page",
                "description": "A sub page",
                "hero_title": "A sub page",
            },
        },
    )
    assert resp.status_code == 201
    assert resp.json() == {"message": "Resource Created"}
    async with uow as uow:
        page: DraftPage[Any] = (await uow.drafts.by_path("/home/test")).unwrap()
        assert page.page.dict() == {
            "slug": "test",
            "title": "sub Page",
            "description": "A sub page",
            "hero_title": "A sub page",
            "intro": None,
        }

    async with uow as uow:
        pages: Sequence[DraftPage[Any]] = (await uow.drafts.by_parent("/home")).unwrap()
        pages_dict = [page.page.dict() for page in pages]
        assert pages_dict == [
            {
                "slug": "test",
                "title": "sub Page",
                "description": "A sub page",
                "hero_title": "A sub page",
                "intro": None,
            }
        ]


async def test_get_draft_403(
    client: TestClient,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.get("/api/drafts/home")
    assert resp.status_code == 403


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/api/drafts/home",
            "response": {
                "metadata": {
                    "type": "blog:HomePage",
                    "path": "/home",
                    "breadcrumb": [
                        {
                            "slug": "home",
                            "title": "hello world - casualcms",
                            "path": "/home",
                        }
                    ],
                },
                "slug": "home",
                "title": "hello world - casualcms",
                "description": "I am so glad to be there",
                "hero_title": "Welcome aboard!",
                "body": [],
            },
        },
        {
            "path": "/api/drafts/home/sub",
            "response": {
                "metadata": {
                    "type": "blog:CategoryPage",
                    "path": "/home/sub",
                    "breadcrumb": [
                        {
                            "slug": "home",
                            "title": "hello world - casualcms",
                            "path": "/home",
                        },
                        {
                            "slug": "sub",
                            "title": "a sub page",
                            "path": "/home/sub",
                        },
                    ],
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
async def test_get_draft(
    params: Mapping[str, Any],
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
    draft_subpage: DraftPage[CategoryPage],
    uow: AbstractUnitOfWork,
):
    resp = client.get(
        params["path"],
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.json() == params["response"]


async def test_preview_draft_403(
    client: TestClient,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.get("/api/previews/home")
    assert resp.status_code == 403


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/api/previews/home",
            "response": {},
        },
    ],
)
async def test_preview_draft(
    params: Mapping[str, Any],
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
    draft_subpage: DraftPage[CategoryPage],
    uow: AbstractUnitOfWork,
):
    resp = client.get(
        params["path"],
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert "<title>hello world - casualcms</title>" in resp.text
    assert "<h2>Welcome aboard!</h2>" in resp.text


async def test_update_home_draft_content_403(
    client: TestClient, draft_hp: DraftPage[HomePage]
):
    payload = {
        "slug": "new-home",
        "title": "new title",
        "description": "new description",
        "hero_title": "New hero title",
        "body": [{"body": "my new body"}],
    }
    resp = client.patch(
        f"/api/drafts/{draft_hp.path}",
        json=payload,
    )
    assert resp.status_code == 403


async def test_update_home_draft_content(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
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
        f"/api/drafts/{draft_hp.path}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=payload,
    )
    assert resp.status_code == 202
    assert resp.json() == {"message": "Resource Updated"}
    async with uow as uow:
        saved_home: DraftPage[HomePage] = (
            await uow.drafts.by_path("/new-home")
        ).unwrap()  # type: ignore

    assert saved_home.slug == "new-home"
    assert saved_home.title == payload["title"]
    assert saved_home.description == payload["description"]
    assert saved_home.page.hero_title == payload["hero_title"]
    assert (
        saved_home.page.body == payload["body"]
    )  # XXX should be a list[Paragraph] here


async def test_update_sub_draft_content(
    client: TestClient,
    authntoken: AuthnToken,
    draft_subpage: DraftPage[CategoryPage],
    uow: AbstractUnitOfWork,
):
    payload = {
        "slug": "new-slug",
        "title": "new title",
    }
    resp = client.patch(
        f"/api/drafts/{draft_subpage.path}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=payload,
    )
    assert resp.status_code == 202
    assert resp.json() == {"message": "Resource Updated"}
    async with uow as uow:
        saved_home = cast(
            HomePage,
            (await uow.drafts.by_path("/home/new-slug")).unwrap(),
        )
    assert saved_home.slug == "new-slug"
    assert saved_home.title == payload["title"]


async def test_delete_draft_403(
    client: TestClient,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.delete(f"/api/drafts/{draft_hp.path}")
    assert resp.status_code == 403


async def test_delete_page(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/drafts/{draft_hp.path}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 204

    async with uow as uow:
        saved_home: DraftRepositoryResult[Any] = await uow.drafts.by_path("/home")

    assert saved_home.is_err()
    assert saved_home.unwrap_err().name == "page_not_found"


async def test_delete_page_422(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[HomePage],
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/drafts/{draft_hp.path}/unkwon",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [{"loc": ["querystring", "path"], "msg": "Unknown page"}]
    }
