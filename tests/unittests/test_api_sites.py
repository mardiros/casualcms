from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page
from casualcms.domain.model.site import Site


async def test_api_list_sites(
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
    default_site: Site,
):
    resp = client.get(
        "/api/sites",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "hostname": default_site.hostname,
            "default": True,
            "root_page_path": home_page.path,
        }
    ]
