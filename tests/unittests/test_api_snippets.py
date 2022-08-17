from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.service.unit_of_work import AbstractUnitOfWork


async def test_api_create_snippet_unauthenticated(
    client: TestClient, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/snippets",
        headers={},
        json={"type": "blog:HeaderSnippet", "payload": {}},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_create_snippet(
    client: TestClient, authntoken: AuthnToken, uow: AbstractUnitOfWork
):
    resp = client.post(
        "/api/snippets",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "type": "blog:HeaderSnippet",
            "payload": {
                "slug": "header",
                "title": "My Blog",
                "links": [{"title": "cat", "href": "/cats"}],
            },
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"slug": "header", "meta": {"type": "blog:HeaderSnippet"}}
    async with uow as uow:
        page = (await uow.snippets.by_slug("header")).unwrap()
        assert page.dict() == {
            "slug": "header",
            "title": "My Blog",
            "links": [{"title": "cat", "href": "/cats"}],
        }
