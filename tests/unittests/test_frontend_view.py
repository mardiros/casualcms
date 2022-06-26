from typing import Any
from fastapi.testclient import TestClient


from .fixtures import RootPage


async def test_get_home_page(client: TestClient, home_page: RootPage):

    resp = client.get("/")
    assert resp.status_code == 200
    assert "<h1>Welcome aboard!</h1>" in resp.text
