from fastapi.testclient import TestClient
from pydantic import Field

from casualcms.domain.model import Page
from casualcms.domain.model.account import AuthnToken
from casualcms.service.unit_of_work import AbstractUnitOfWork


class DummiesPage(Page):
    body: str = Field(...)


async def test_api_create_page_unauthenticated(
    client: TestClient, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/pages",
        headers={},
        json={
            "type": "tests.unittests.test_api_pages:DummiesPage",
            "payload": {
                "id": "abc",
                "slug": "/",
                "title": "Root Page",
                "description": "The home page",
                "body": "lorem ipsum",
            },
        },
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
            "type": "tests.unittests.test_api_pages:DummiesPage",
            "payload": {
                "id": "abc",
                "slug": "/",
                "title": "Root Page",
                "description": "The home page",
                "body": "lorem ipsum",
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"href": "/"}
