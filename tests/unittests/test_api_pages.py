from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.site import Site

from ..casualblog.models import HomePage


async def test_publish(
    client: TestClient, authntoken: AuthnToken, draft_hp: HomePage, default_site: Site
):

    resp = client.post(
        "/api/pages",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={"path": draft_hp.metadata.path, "hostname": default_site.hostname},
    )
    assert resp.status_code == 201
    assert resp.json() == {"message": "Resource Created"}


async def test_publish_422(client: TestClient, authntoken: AuthnToken):

    resp = client.post(
        "/api/pages",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={},
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [
            {
                "input": None,
                "loc": ["body", "hostname"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.3/v/missing",
            },
            {
                "input": None,
                "loc": ["body", "path"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.3/v/missing",
            },
        ],
    }


async def test_publish_403(
    client: TestClient, authntoken: AuthnToken, draft_hp: HomePage, default_site: Site
):

    resp = client.post(
        "/api/pages",
        json={"draft_id": draft_hp.metadata.path, "site_id": default_site.hostname},
    )
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}
