from fastapi.testclient import TestClient

from casualcms.domain.model import Site

from ..casualblog.models import HomePage


async def test_get_home_page(
    client: TestClient, home_page: HomePage, default_site: Site
):
    resp = client.get("/", headers={"Host": "www.example.net"})
    assert resp.status_code == 200
    assert "<h1>Welcome aboard!</h1>" in resp.text
