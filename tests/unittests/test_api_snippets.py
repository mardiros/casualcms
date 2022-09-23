from typing import cast

from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.service.unit_of_work import AbstractUnitOfWork

from ..casualblog.models import FooterSnippet, HeaderSnippet


async def test_api_create_snippet_403(client: TestClient, uow: AbstractUnitOfWork):
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
                "key": "header",
                "title": "My Blog",
                "links": [{"title": "cat", "href": "/cats"}],
            },
        },
    )
    assert resp.status_code == 201
    assert resp.json() == {"key": "header", "meta": {"type": "blog:HeaderSnippet"}}
    async with uow as uow:
        snippet = (await uow.snippets.by_key("header")).unwrap()
        assert snippet.dict() == {
            "key": "header",
            "title": "My Blog",
            "links": [{"title": "cat", "href": "/cats"}],
        }


async def test_api_list_snippet_403(client: TestClient, uow: AbstractUnitOfWork):
    resp = client.get(
        "/api/snippets",
        headers={},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_list_snippet(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    alt_header_snippet: HeaderSnippet,
    footer_snippet: FooterSnippet,
):
    resp = client.get(
        "/api/snippets",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"meta": {"type": "blog:HeaderSnippet"}, "key": "alt-header"},
        {"meta": {"type": "tests.casualblog.models:FooterSnippet"}, "key": "footer"},
        {"meta": {"type": "blog:HeaderSnippet"}, "key": "header"},
    ]


async def test_api_list_snippet_filter(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    alt_header_snippet: HeaderSnippet,
    footer_snippet: FooterSnippet,
):
    resp = client.get(
        "/api/snippets?type=blog:HeaderSnippet",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"meta": {"type": "blog:HeaderSnippet"}, "key": "alt-header"},
        {"meta": {"type": "blog:HeaderSnippet"}, "key": "header"},
    ]


async def test_api_patch_snippet_403(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.patch(
        "/api/snippets/header",
        json={
            "key": "new-key",
            "title": "new title",
        },
    )
    assert resp.status_code == 403


async def test_api_patch_snippet(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.patch(
        "/api/snippets/header",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "key": "new-key",
            "title": "new title",
        },
    )
    assert resp.status_code == 202
    assert resp.json() == {"meta": {"type": "blog:HeaderSnippet"}, "key": "new-key"}

    async with uow as uow:
        snip = await uow.snippets.by_key("new-key")
        assert snip.is_ok()
        snipok = cast(HeaderSnippet, snip.unwrap())
        assert snipok.title == "new title"

        snip = await uow.snippets.by_key("header")
        assert snip.is_err()
        assert snip.unwrap_err().name == "snippet_not_found"


async def test_api_get_snippet_403(
    client: TestClient,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.get("/api/snippets/header")
    assert resp.status_code == 403


async def test_api_get_snippet(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.get(
        "/api/snippets/header",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "links": [
            {"href": "/cats", "title": "cats"},
            {"href": "/dogs", "title": "dogs"},
        ],
        "meta": {"type": "blog:HeaderSnippet"},
        "key": "header",
        "title": "A personal blog",
    }


async def test_api_delete_snippet_403(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.delete("/api/snippets/header")
    assert resp.status_code == 403


async def test_api_delete_snippet(
    client: TestClient,
    authntoken: AuthnToken,
    header_snippet: HeaderSnippet,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        "/api/snippets/header",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 204
    assert resp.text == ""

    async with uow as uow:
        snip = await uow.snippets.by_key("header")
        assert snip.is_err()
        assert snip.unwrap_err().name == "snippet_not_found"
