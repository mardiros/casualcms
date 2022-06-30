from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page
from casualcms.service.unit_of_work import AbstractUnitOfWork


async def test_api_create_page_unauthenticated(
    client: TestClient, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/pages",
        headers={},
        json={"type": "tests.unittests.fixtures:RootPage", "payload": {}},
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
            "type": "tests.unittests.fixtures:RootPage",
            "payload": {
                "id": "abc",
                "slug": "/",
                "title": "Root Page",
                "description": "The home page",
                "hero_title": "You are awesome",
                "body": [{"body": "lorem ipsum"}],
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"href": "/"}
    async with uow as uow:
        page = (await uow.pages.by_path("/")).unwrap()
        assert page.dict() == {
            "id": "abc",
            "slug": "/",
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
            "path": home_page.path,
        }
    ]
