from fastapi.testclient import TestClient

from ..casualblog.models import HomePage


async def test_get_home_page(client: TestClient, home_page: HomePage):

    resp = client.get("/home")  # FIXME
    assert resp.status_code == 200
    assert "<h1>Welcome aboard!</h1>" in resp.text
