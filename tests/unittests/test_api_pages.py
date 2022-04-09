from fastapi.testclient import TestClient
from pydantic import Field

from casualcms.domain.model import Page
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


class DummiesPage(Page):
    body: str = Field(...)


async def test_api_create_page(
    client: TestClient, messagebus: MessageRegistry, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/pages",
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
