from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken


async def test_list_types(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/snippets-types",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    # assert resp.status_code == 200
    assert resp.json() == [
        {"type": "blog:HeaderSnippet"},
        {"type": "tests.casualblog.models:FooterSnippet"},
    ]
