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
        json={"draft_id": draft_hp.id, "site_id": default_site.id},
    )
    assert resp.status_code == 201
    assert resp.json() == {"href": "/"}


async def test_publish_403(
    client: TestClient, authntoken: AuthnToken, draft_hp: HomePage, default_site: Site
):

    resp = client.post(
        "/api/pages",
        headers={},
        json={"draft_id": draft_hp.id, "site_id": default_site.id},
    )
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}
