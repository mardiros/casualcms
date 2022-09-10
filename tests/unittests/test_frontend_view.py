from fastapi.testclient import TestClient

from casualcms.domain.model import Site

from ..casualblog.models import HeaderSnippet, HomePage


async def test_get_draft_hp(
    client: TestClient,
    draft_hp: HomePage,
    default_site: Site,
    header_snippet: HeaderSnippet,
):
    resp = client.get("/", headers={"Host": "www.example.net"})
    assert resp.status_code == 200
    assert "<h1>A personal blog</h1>" in resp.text
    assert "<h2>Welcome aboard!</h2>" in resp.text


async def test_get_assets(
    client: TestClient,
):
    resp = client.get("/assets/my.css", headers={"Host": "www.example.net"})
    assert resp.status_code == 200
    assert "background-color: cornsilk" in resp.text
