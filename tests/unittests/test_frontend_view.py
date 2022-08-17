from fastapi.testclient import TestClient

from casualcms.domain.model import Site

from ..casualblog.models import HeaderSnippet, HomePage


async def test_get_home_page(
    client: TestClient,
    home_page: HomePage,
    default_site: Site,
    header_snippet: HeaderSnippet,
):
    resp = client.get("/", headers={"Host": "www.example.net"})
    assert resp.status_code == 200
    assert "<h1>A personal blog</h1>" in resp.text
    assert "<h2>Welcome aboard!</h2>" in resp.text
